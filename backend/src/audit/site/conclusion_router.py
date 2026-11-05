"""Подготовка, передача и приёмка заключения."""

from fastapi import APIRouter, Depends, File, UploadFile

from src.audit.schemas.audit import AuditResponse
from src.audit.site.conclusion_dependencies import (
    get_accept_work_audit_usecase,
    get_mark_conclusion_ready_audit_usecase,
    get_send_conclusion_audit_usecase,
)
from src.audit.site.usecases.accept_work import AcceptAuditWorkUseCase
from src.audit.site.usecases.mark_conclusion_ready import MarkAuditConclusionReadyUseCase
from src.audit.site.usecases.send_conclusion import SendAuditConclusionUseCase
from src.auth.site.dependencies import require_customer, require_expert
from src.users.models.user import User

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
)


@router.post("/{audit_id}/conclusion-ready")
async def mark_conclusion_ready(
    *,
    audit_id: int,
    user: User = Depends(require_expert),
    usecase: MarkAuditConclusionReadyUseCase = Depends(get_mark_conclusion_ready_audit_usecase),
) -> AuditResponse:
    """Сообщить о готовности заключения."""

    return await usecase.execute(
        audit_id=audit_id,
        user=user,
    )


@router.post("/{audit_id}/accept-work")
async def accept_work(
    *,
    audit_id: int,
    user: User = Depends(require_customer),
    usecase: AcceptAuditWorkUseCase = Depends(get_accept_work_audit_usecase),
) -> AuditResponse:
    """Принять выполненную работу."""

    return await usecase.execute(
        audit_id=audit_id,
        user=user,
    )


@router.post("/{audit_id}/conclusion")
async def send_conclusion(
    *,
    audit_id: int,
    user: User = Depends(require_expert),
    usecase: SendAuditConclusionUseCase = Depends(get_send_conclusion_audit_usecase),
    files: list[UploadFile] = File(default=[]),
) -> AuditResponse:
    """Передать заключение заказчику."""

    return await usecase.execute(
        audit_id=audit_id,
        user=user,
        files=files,
    )
