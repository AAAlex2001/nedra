"""Счета и оплата."""

from fastapi import APIRouter, Depends, Response

from src.audit.site.payment_dependencies import (
    get_act_usecase,
    get_audit_payments_usecase,
    get_issue_invoice_usecase,
)
from src.audit.site.schemas.audit_payments import AuditPaymentsResponse
from src.audit.site.usecases.get_act import GetAuditActUseCase
from src.audit.site.usecases.get_audit_payments import GetAuditPaymentsUseCase
from src.audit.site.usecases.issue_invoice import IssueAuditInvoiceUseCase
from src.auth.site.dependencies import get_current_user, require_customer
from src.billing.schemas.invoice import InvoiceResponse
from src.documents.http_response import document_response
from src.users.models.user import User

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
)


@router.get("/{audit_id}/payments")
async def get_audit_payments(
    *,
    audit_id: int,
    user: User = Depends(get_current_user),
    usecase: GetAuditPaymentsUseCase = Depends(get_audit_payments_usecase),
) -> AuditPaymentsResponse:
    """Оплата аудита."""

    return await usecase.execute(
        audit_id=audit_id,
        user=user,
    )


@router.post("/{audit_id}/invoice")
async def issue_invoice(
    *,
    audit_id: int,
    user: User = Depends(require_customer),
    usecase: IssueAuditInvoiceUseCase = Depends(get_issue_invoice_usecase),
) -> InvoiceResponse:
    """Получить счёт на текущий этап."""

    return await usecase.execute(
        audit_id=audit_id,
        user=user,
    )


@router.get("/{audit_id}/act")
async def get_act(
    *,
    audit_id: int,
    user: User = Depends(require_customer),
    usecase: GetAuditActUseCase = Depends(get_act_usecase),
) -> Response:
    """Скачать акт выполненных работ."""

    document = await usecase.execute(
        audit_id=audit_id,
        user=user,
    )
    return document_response(document=document)
