"""Просмотр счетов заказчика."""

from src.billing.repositories.invoices import InvoiceRepository
from src.billing.schemas.invoice import InvoiceResponse


class ListInvoicesUseCase:
    """Список своих счетов."""

    def __init__(self, *, invoices: InvoiceRepository) -> None:
        """Счета."""

        self.invoices = invoices

    async def execute(self, *, user_id: int) -> list[InvoiceResponse]:
        """Получить счета заказчика."""

        invoices = await self.invoices.list_for_customer(user_id=user_id)
        return [InvoiceResponse.from_model(invoice=invoice) for invoice in invoices]
