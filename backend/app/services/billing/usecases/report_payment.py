"""Сценарий: заказчик сообщает, что оплатил счёт со своего расчётного счёта."""

from datetime import datetime, timezone

from app.models.billing import Invoice
from app.models.expertise import Expertise
from app.models.user import User
from app.services.billing.exceptions import InvoiceAlreadyPaidError, InvoiceNotFoundError
from app.services.billing.repo import InvoiceRepository
from app.services.expertise.repo import ExpertiseRepository


class ReportInvoicePaidUseCase:
    """Отметить, что заказчик заявил об оплате счёта.

    Деньги идут мимо сайта, поэтому это только сигнал администратору:
    статус экспертизы двигает всё равно он, когда увидит поступление в банке.
    """

    def __init__(self, invoices: InvoiceRepository, expertises: ExpertiseRepository) -> None:
        self.invoices = invoices
        self.expertises = expertises

    async def execute(self, customer: User, invoice_id: int) -> Invoice:
        """Бросает InvoiceNotFoundError и InvoiceAlreadyPaidError."""

        invoice = await self.invoices.get_by_id(invoice_id)
        if invoice is None:
            raise InvoiceNotFoundError(f"Счёт {invoice_id} не найден")

        expertise = await self.expertises.get_by_id(invoice.expertise_id)
        if expertise is None or expertise.customer_id != customer.id:
            raise InvoiceNotFoundError(f"Счёт {invoice_id} не найден")

        if invoice.paid_at is not None:
            raise InvoiceAlreadyPaidError("Оплата по счёту уже подтверждена")

        if invoice.reported_at is not None:
            return invoice

        invoice.reported_at = datetime.now(timezone.utc)

        return await self.invoices.save(invoice)


def invoice_expertise(expertise: Expertise) -> str:
    """Короткое описание заявки для письма администратору."""

    return f"Заявка №{expertise.id}, область {expertise.area_code}"
