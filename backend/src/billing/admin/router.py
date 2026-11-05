"""Проверка оплаты администратором."""

from fastapi import APIRouter, Depends

from src.auth.admin.access import require_admin
from src.billing.admin.dependencies import (
    get_confirm_invoice_payment_usecase,
    get_list_admin_invoices_usecase,
)
from src.billing.admin.usecases.confirm_invoice_payment import ConfirmInvoicePaymentUseCase
from src.billing.admin.usecases.list_invoices import ListAdminInvoicesUseCase
from src.billing.schemas.invoice import InvoiceResponse

router = APIRouter(
    prefix="/admin/invoices",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


@router.get("")
async def list_invoices(
    *, usecase: ListAdminInvoicesUseCase = Depends(get_list_admin_invoices_usecase)
) -> list[InvoiceResponse]:
    """Получить счета для проверки."""

    return await usecase.execute()


@router.post("/{invoice_id}/pay")
async def confirm_invoice_payment(
    *,
    invoice_id: int,
    usecase: ConfirmInvoicePaymentUseCase = Depends(get_confirm_invoice_payment_usecase),
) -> InvoiceResponse:
    """Подтвердить банковский перевод."""

    return await usecase.execute(invoice_id=invoice_id)
