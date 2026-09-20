from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.admin import require_admin
from app.dependencies.billing import get_confirm_invoice_usecase, get_invoice_repository
from app.routers.billing import to_invoice_schema
from app.schemas.billing import InvoiceOutSchema
from app.services.billing.exceptions import InvoiceAlreadyPaidError, InvoiceNotFoundError
from app.services.billing.repo import InvoiceRepository
from app.services.billing.usecases.confirm_invoice import ConfirmInvoiceUseCase


router = APIRouter(
    prefix="/admin/invoices",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


@router.get("")
async def list_invoices(
    invoices: InvoiceRepository = Depends(get_invoice_repository),
) -> list[InvoiceOutSchema]:
    """Все счета, новые первыми."""

    items = await invoices.list_all()

    return [to_invoice_schema(item) for item in items]


@router.post("/{invoice_id}/pay")
async def confirm_invoice(
    invoice_id: int,
    usecase: ConfirmInvoiceUseCase = Depends(get_confirm_invoice_usecase),
) -> InvoiceOutSchema:
    """Отметить счёт оплаченным: деньги пришли на расчётный счёт."""

    try:
        invoice = await usecase.execute(invoice_id)
    except InvoiceNotFoundError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error
    except InvoiceAlreadyPaidError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from error

    return to_invoice_schema(invoice)
