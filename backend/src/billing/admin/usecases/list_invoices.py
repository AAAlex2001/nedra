"""Просмотр всех счетов администратором."""

from src.billing.repositories.invoices import InvoiceRepository
from src.billing.schemas.invoice import InvoiceResponse


class ListAdminInvoicesUseCase:
    """Счета для проверки поступлений."""

    def __init__(self, *, invoices: InvoiceRepository) -> None:
        """Счета."""

        self.invoices = invoices

    async def execute(self) -> list[InvoiceResponse]:
        """Получить все счета."""

        invoices = await self.invoices.list_all()
        return [InvoiceResponse.from_model(invoice=invoice) for invoice in invoices]
