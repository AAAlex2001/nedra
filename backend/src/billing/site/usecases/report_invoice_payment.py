"""Сообщение заказчика об оплате счёта."""

from datetime import UTC, datetime
from typing import Literal

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.billing.exceptions import InvoiceAlreadyPaidError, InvoiceNotFoundError
from src.billing.invoice_attachments import InvoiceAttachments
from src.billing.invoice_letters import InvoiceLetters
from src.billing.repositories.invoices import InvoiceRepository
from src.billing.schemas.invoice import InvoiceResponse
from src.notifications.models.notification import Notification
from src.notifications.repositories.notifications import NotificationRepository


class ReportInvoicePaymentUseCase:
    """Заявленная оплата без подтверждения поступления."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        invoices: InvoiceRepository,
        attachments: InvoiceAttachments,
        notifications: NotificationRepository,
        letters: InvoiceLetters,
    ) -> None:
        """Счета, файлы и уведомления."""

        self.session = session
        self.invoices = invoices
        self.attachments = attachments
        self.notifications = notifications
        self.letters = letters

    async def execute(
        self,
        *,
        invoice_id: int,
        user_id: int,
        document: UploadFile | None,
        document_kind: Literal["payment_order", "guarantee_letter"],
    ) -> InvoiceResponse:
        """Сообщить об оплате и приложить подтверждение."""

        invoice = await self.invoices.get_for_update(invoice_id=invoice_id)
        if invoice is None or not await self.invoices.belongs_to_customer(
            invoice_id=invoice_id,
            user_id=user_id,
        ):
            raise InvoiceNotFoundError()

        if invoice.paid_at is not None:
            raise InvoiceAlreadyPaidError()

        first_report = invoice.reported_at is None
        saved_file = None
        try:
            if document is not None:
                saved_file = await self.attachments.save(
                    invoice=invoice,
                    file=document,
                    kind=document_kind,
                    user_id=user_id,
                )

            if first_report:
                invoice.reported_at = datetime.now(UTC)
                executor_id = await self.invoices.get_executor_id(invoice_id=invoice_id)
                if executor_id is not None:
                    await self.notifications.add(
                        notification=Notification(
                            user_id=executor_id,
                            audit_id=invoice.audit_id,
                            expertise_id=invoice.expertise_id,
                            kind="check_payment",
                            text=f"Заказчик сообщил об оплате счёта №{invoice.id}",
                        )
                    )

            await self.invoices.save(invoice=invoice)
            response = InvoiceResponse.from_model(invoice=invoice)
        except Exception:
            try:
                await self.session.rollback()
            finally:
                if saved_file is not None:
                    await self.attachments.remove(file=saved_file)
            raise

        await self.session.commit()
        if first_report:
            await self.letters.send_payment_report(invoice=invoice)
        return response
