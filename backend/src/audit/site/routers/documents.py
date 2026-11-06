"""Документы и замечания."""

from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, Response, UploadFile
from fastapi.responses import FileResponse

from src.audit.options import AUDIT_DOCUMENTS
from src.audit.schemas.audit import AuditResponse
from src.audit.site.dependencies.documents import (
    get_audit_document_usecase,
    get_audit_documents_report_usecase,
    get_list_audit_documents_usecase,
    get_list_audit_remarks_usecase,
    get_upload_audit_documents_usecase,
)
from src.audit.site.schemas.audit_checklist import AuditChecklistItemResponse
from src.audit.site.schemas.audit_documents import (
    AuditDocumentResponse,
    AuditRemarkResponse,
)
from src.audit.site.usecases.get_audit_document import GetAuditDocumentUseCase
from src.audit.site.usecases.get_audit_documents_report import (
    GetAuditDocumentsReportUseCase,
)
from src.audit.site.usecases.list_audit_documents import ListAuditDocumentsUseCase
from src.audit.site.usecases.list_audit_remarks import ListAuditRemarksUseCase
from src.audit.site.usecases.upload_audit_documents import UploadAuditDocumentsUseCase
from src.auth.site.dependencies.authentication import get_current_user, require_customer
from src.users.models.user import User

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
)


@router.post("/{audit_id}/documents")
async def upload_audit_documents(
    *,
    audit_id: int,
    files: list[UploadFile] = File(default=[]),
    items: list[int] = Form(default=[]),
    user: User = Depends(require_customer),
    usecase: UploadAuditDocumentsUseCase = Depends(get_upload_audit_documents_usecase),
) -> AuditResponse:
    """Загрузить документы по перечню."""

    return await usecase.execute(
        user=user,
        audit_id=audit_id,
        files=files,
        item_numbers=items,
    )


@router.get("/{audit_id}/documents-report")
async def get_audit_documents_report(
    *,
    audit_id: int,
    user: User = Depends(get_current_user),
    usecase: GetAuditDocumentsReportUseCase = Depends(get_audit_documents_report_usecase),
) -> Response:
    """Скачать отчёт о комплектности документов."""

    document = await usecase.execute(
        audit_id=audit_id,
        user=user,
    )

    return Response(
        content=document.content,
        media_type=document.content_type,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(document.filename)}"},
    )


@router.get("/checklist")
async def get_audit_checklist() -> list[AuditChecklistItemResponse]:
    """Получить перечень документов для аудита."""

    return [
        AuditChecklistItemResponse(
            number=number,
            title=title,
        )
        for number, title in enumerate(AUDIT_DOCUMENTS, start=1)
    ]


@router.get("/{audit_id}/documents/{document_id}")
async def get_audit_document(
    *,
    audit_id: int,
    document_id: int,
    user: User = Depends(get_current_user),
    usecase: GetAuditDocumentUseCase = Depends(get_audit_document_usecase),
) -> FileResponse:
    """Скачать документ."""

    path, filename = await usecase.execute(
        audit_id=audit_id,
        document_id=document_id,
        user=user,
    )
    return FileResponse(path, filename=filename)


@router.get("/{audit_id}/documents")
async def list_audit_documents(
    *,
    audit_id: int,
    user: User = Depends(get_current_user),
    usecase: ListAuditDocumentsUseCase = Depends(get_list_audit_documents_usecase),
) -> list[AuditDocumentResponse]:
    """Список документов аудита."""

    return await usecase.execute(
        audit_id=audit_id,
        user=user,
    )


@router.get("/{audit_id}/remarks")
async def list_audit_remarks(
    *,
    audit_id: int,
    user: User = Depends(get_current_user),
    usecase: ListAuditRemarksUseCase = Depends(get_list_audit_remarks_usecase),
) -> list[AuditRemarkResponse]:
    """Замечания руководителя."""

    return await usecase.execute(
        audit_id=audit_id,
        user=user,
    )
