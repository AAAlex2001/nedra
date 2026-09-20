"""Сценарий подтверждения оплаты по счёту администратором."""

from datetime import datetime, timezone

from app.models.billing import Invoice, InvoiceStage
from app.models.notification import Notification
from app.services.billing.exceptions import InvoiceAlreadyPaidError, InvoiceNotFoundError
from app.services.billing.repo import InvoiceRepository
from app.services.expertise.repo import ExpertiseRepository
from app.services.expertise.stages import mark_stage_paid
from app.services.notifications.repo import NotificationRepository


class ConfirmInvoiceUseCase:
    """Отметить счёт оплаченным и сдвинуть экспертизу на следующий шаг.

    Деньги приходят на расчётный счёт, поэтому факт оплаты подтверждает
    администратор, когда видит поступление в банке.
    """

    def __init__(
        self,
        invoices: InvoiceRepository,
        expertises: ExpertiseRepository,
        notifications: NotificationRepository,
    ) -> None:
        self.invoices = invoices
        self.expertises = expertises
        self.notifications = notifications

    async def execute(self, invoice_id: int) -> Invoice:
        """Бросает InvoiceNotFoundError и InvoiceAlreadyPaidError."""

        invoice = await self.invoices.get_by_id(invoice_id)
        if invoice is None:
            raise InvoiceNotFoundError(f"Счёт {invoice_id} не найден")

        if invoice.paid_at is not None:
            raise InvoiceAlreadyPaidError("Счёт уже отмечен оплаченным")

        invoice.paid_at = datetime.now(timezone.utc)

        expertise = await self.expertises.get_by_id(invoice.expertise_id)
        if expertise is not None and expertise.expert_id is not None:
            text = mark_stage_paid(expertise, InvoiceStage(invoice.stage))

            if text is not None:
                self.notifications.add_all(
                    [
                        Notification(
                            user_id=expertise.expert_id,
                            expertise_id=expertise.id,
                            text=text,
                        )
                    ]
                )

        return await self.invoices.save(invoice)
