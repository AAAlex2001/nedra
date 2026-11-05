"""Счета заказчика."""

from typing import Literal

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import Response

from src.auth.site.dependencies import require_customer
from src.billing.schemas.invoice import InvoiceResponse
from src.billing.site.dependencies import (
    get_invoice_document_usecase,
    get_list_invoices_usecase,
    get_report_invoice_payment_usecase,
)
from src.billing.site.usecases.get_invoice_document import GetInvoiceDocumentUseCase
from src.billing.site.usecases.list_invoices import ListInvoicesUseCase
from src.billing.site.usecases.report_invoice_payment import ReportInvoicePaymentUseCase
from src.documents.http_response import document_response
from src.users.models.user import User

router = APIRouter(
    prefix="/invoices",
    tags=["billing"],
)


@router.get("")
async def list_invoices(
    *,
    user: User = Depends(require_customer),
    usecase: ListInvoicesUseCase = Depends(get_list_invoices_usecase),
) -> list[InvoiceResponse]:
    """Получить свои счета."""

    return await usecase.execute(user_id=user.id)


@router.post("/{invoice_id}/paid")
async def report_invoice_payment(
    *,
    invoice_id: int,
    user: User = Depends(require_customer),
    document: UploadFile | None = File(default=None),
    document_kind: Literal["payment_order", "guarantee_letter"] = Form(default="payment_order"),
    usecase: ReportInvoicePaymentUseCase = Depends(get_report_invoice_payment_usecase),
) -> InvoiceResponse:
    """Сообщить об оплате счёта."""

    return await usecase.execute(
        invoice_id=invoice_id,
        user_id=user.id,
        document=document,
        document_kind=document_kind,
    )


@router.get("/{invoice_id}/pdf")
async def get_invoice_document(
    *,
    invoice_id: int,
    user: User = Depends(require_customer),
    usecase: GetInvoiceDocumentUseCase = Depends(get_invoice_document_usecase),
) -> Response:
    """Скачать свой счёт."""

    document = await usecase.execute(
        invoice_id=invoice_id,
        user_id=user.id,
    )
    return document_response(document=document)
