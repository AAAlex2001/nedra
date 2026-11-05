"""Счета и оплата."""

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from src.auth.site.dependencies import get_current_user, require_customer
from src.billing.schemas.invoice import InvoiceResponse
from src.documents.http_response import document_response
from src.expertise.site.billing_dependencies import (
    get_act_usecase,
    get_expertise_payments_usecase,
    get_issue_invoice_usecase,
)
from src.expertise.site.schemas.expertise_payments import ExpertisePaymentsResponse
from src.expertise.site.usecases.get_act import GetExpertiseActUseCase
from src.expertise.site.usecases.get_expertise_payments import GetExpertisePaymentsUseCase
from src.expertise.site.usecases.issue_invoice import IssueExpertiseInvoiceUseCase
from src.users.models.user import User

router = APIRouter(
    prefix="/expertises",
    tags=["expertise"],
)


@router.get("/{expertise_id}/payments")
async def get_expertise_payments(
    *,
    expertise_id: int,
    user: User = Depends(get_current_user),
    usecase: GetExpertisePaymentsUseCase = Depends(get_expertise_payments_usecase),
) -> ExpertisePaymentsResponse:
    """Получить сведения об оплате."""

    return await usecase.execute(
        expertise_id=expertise_id,
        user=user,
    )


@router.post("/{expertise_id}/invoice")
async def issue_invoice(
    *,
    expertise_id: int,
    user: User = Depends(require_customer),
    usecase: IssueExpertiseInvoiceUseCase = Depends(get_issue_invoice_usecase),
) -> InvoiceResponse:
    """Получить счёт на текущий этап."""

    return await usecase.execute(
        expertise_id=expertise_id,
        user=user,
    )


@router.get("/{expertise_id}/act")
async def get_act(
    *,
    expertise_id: int,
    user: User = Depends(require_customer),
    usecase: GetExpertiseActUseCase = Depends(get_act_usecase),
) -> Response:
    """Скачать акт выполненных работ."""

    document = await usecase.execute(
        expertise_id=expertise_id,
        user=user,
    )
    return document_response(document=document)
