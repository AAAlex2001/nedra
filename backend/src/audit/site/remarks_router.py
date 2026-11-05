"""Замечания и исправленные документы."""

from fastapi import APIRouter, Depends, File, Form, UploadFile

from src.audit.schemas.audit import AuditResponse
from src.audit.site.remarks_dependencies import (
    get_resubmit_documents_audit_usecase,
    get_send_remarks_audit_usecase,
)
from src.audit.site.usecases.resubmit_documents import ResubmitAuditDocumentsUseCase
from src.audit.site.usecases.send_remarks import SendAuditRemarksUseCase
from src.auth.site.dependencies import require_customer, require_expert
from src.users.models.user import User

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
)


@router.post("/{audit_id}/remarks")
async def send_remarks(
    *,
    audit_id: int,
    user: User = Depends(require_expert),
    usecase: SendAuditRemarksUseCase = Depends(get_send_remarks_audit_usecase),
    files: list[UploadFile] = File(default=[]),
    text: str | None = Form(default=None),
) -> AuditResponse:
    """Отправить замечания заказчику."""

    return await usecase.execute(
        audit_id=audit_id,
        user=user,
        files=files,
        text=text,
    )


@router.post("/{audit_id}/revision")
async def resubmit_documents(
    *,
    audit_id: int,
    user: User = Depends(require_customer),
    usecase: ResubmitAuditDocumentsUseCase = Depends(get_resubmit_documents_audit_usecase),
    files: list[UploadFile] = File(default=[]),
    text: str | None = Form(default=None),
) -> AuditResponse:
    """Отправить исправленные документы."""

    return await usecase.execute(
        audit_id=audit_id,
        user=user,
        files=files,
        text=text,
    )
