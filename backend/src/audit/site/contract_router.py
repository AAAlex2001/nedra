"""Подготовка и подтверждение договора."""

from typing import Literal

from fastapi import APIRouter, Depends, Response

from src.audit.schemas.audit import AuditResponse
from src.audit.schemas.audit_contract import AuditContractResponse
from src.audit.site.contract_dependencies import (
    get_audit_contract_document_usecase,
    get_audit_contract_usecase,
    get_confirm_audit_contract_usecase,
)
from src.audit.site.usecases.confirm_contract import ConfirmAuditContractUseCase
from src.audit.site.usecases.get_audit_contract import GetAuditContractUseCase
from src.audit.site.usecases.get_contract_document import GetAuditContractDocumentUseCase
from src.auth.site.dependencies import get_current_user, require_customer
from src.documents.http_response import document_response
from src.users.models.user import User

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
)


@router.post("/{audit_id}/confirm")
async def confirm_audit_contract(
    *,
    audit_id: int,
    user: User = Depends(require_customer),
    usecase: ConfirmAuditContractUseCase = Depends(get_confirm_audit_contract_usecase),
) -> AuditResponse:
    """Подтвердить договор и соглашение."""

    return await usecase.execute(
        audit_id=audit_id,
        user=user,
    )


@router.get("/{audit_id}/signing/{kind}")
async def get_audit_contract_document(
    *,
    audit_id: int,
    kind: Literal["contract", "nda"],
    user: User = Depends(get_current_user),
    usecase: GetAuditContractDocumentUseCase = Depends(get_audit_contract_document_usecase),
) -> Response:
    """Скачать договор или соглашение."""

    document = await usecase.execute(
        audit_id=audit_id,
        document_kind=kind,
        user=user,
    )

    return document_response(document=document)


@router.get("/{audit_id}/contract")
async def get_audit_contract(
    *,
    audit_id: int,
    user: User = Depends(get_current_user),
    usecase: GetAuditContractUseCase = Depends(get_audit_contract_usecase),
) -> AuditContractResponse | None:
    """Сведения о договоре."""

    return await usecase.execute(
        audit_id=audit_id,
        user=user,
    )
