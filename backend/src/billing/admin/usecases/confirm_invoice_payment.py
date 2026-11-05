"""Подтверждение банковского перевода."""

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.audit_payment_confirmation import AuditPaymentConfirmation
from src.billing.exceptions import InvoiceAlreadyPaidError, InvoiceNotFoundError
from src.billing.repositories.invoices import InvoiceRepository
from src.billing.schemas.invoice import InvoiceResponse
from src.expertise.expertise_payment_confirmation import ExpertisePaymentConfirmation
from src.payments.enums import PaymentStage


class ConfirmInvoicePaymentUseCase:
    """Счёт и оплаченный этап в одной транзакции."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        invoices: InvoiceRepository,
        audit_confirmation: AuditPaymentConfirmation,
        expertise_confirmation: ExpertisePaymentConfirmation,
    ) -> None:
        """Счета и подтверждение этапов."""

        self.session = session
        self.invoices = invoices
        self.audit_confirmation = audit_confirmation
        self.expertise_confirmation = expertise_confirmation

    async def execute(self, *, invoice_id: int) -> InvoiceResponse:
        """Подтвердить поступление денег."""

        invoice = await self.invoices.get_for_update(invoice_id=invoice_id)
        if invoice is None:
            raise InvoiceNotFoundError()
        if invoice.paid_at is not None:
            raise InvoiceAlreadyPaidError()

        paid_at = datetime.now(UTC)
        if invoice.audit_id is not None:
            await self.audit_confirmation.confirm(
                audit_id=invoice.audit_id,
                stage=PaymentStage(invoice.stage),
                amount=invoice.amount,
                paid_at=paid_at,
            )
        else:
            await self.expertise_confirmation.confirm(
                expertise_id=invoice.expertise_id,
                stage=PaymentStage(invoice.stage),
                amount=invoice.amount,
                paid_at=paid_at,
            )

        invoice.paid_at = paid_at
        await self.invoices.save(invoice=invoice)
        response = InvoiceResponse.from_model(invoice=invoice)
        await self.session.commit()
        return response
