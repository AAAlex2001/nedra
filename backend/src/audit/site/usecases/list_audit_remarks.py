"""Просмотр замечаний руководителя."""

from src.audit.repositories.audit_documents import AuditDocumentRepository
from src.audit.repositories.audit_remarks import AuditRemarkRepository
from src.audit.site.audit_access import AuditAccess
from src.audit.site.schemas.audit_documents import (
    AuditDocumentResponse,
    AuditRemarkResponse,
)
from src.users.models.user import User


class ListAuditRemarksUseCase:
    """Замечания и приложенные файлы."""

    def __init__(
        self,
        *,
        access: AuditAccess,
        remarks: AuditRemarkRepository,
        documents: AuditDocumentRepository,
    ) -> None:
        """Права доступа, замечания и файлы."""

        self.access = access
        self.remarks = remarks
        self.documents = documents

    async def execute(
        self,
        *,
        audit_id: int,
        user: User,
    ) -> list[AuditRemarkResponse]:
        """Получить замечания с приложениями."""

        await self.access.get_visible(
            audit_id=audit_id,
            user=user,
        )
        remarks = await self.remarks.list_for_audit(audit_id=audit_id)
        documents = await self.documents.list_for_remarks(audit_id=audit_id)
        documents_by_remark_id: dict[int, list[AuditDocumentResponse]] = {}

        for document in documents:
            if document.remark_id not in documents_by_remark_id:
                documents_by_remark_id[document.remark_id] = []

            documents_by_remark_id[document.remark_id].append(
                AuditDocumentResponse.from_model(document=document),
            )

        return [
            AuditRemarkResponse.from_model(
                remark=remark,
                documents=documents_by_remark_id.get(remark.id, []),
            )
            for remark in remarks
        ]
