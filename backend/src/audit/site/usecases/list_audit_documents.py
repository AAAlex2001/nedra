"""Просмотр документов аудита."""

from src.audit.repositories.audit_documents import AuditDocumentRepository
from src.audit.site.audit_access import AuditAccess
from src.audit.site.schemas.audit_documents import AuditDocumentResponse
from src.users.models.user import User


class ListAuditDocumentsUseCase:
    """Список файлов аудита."""

    def __init__(
        self,
        *,
        access: AuditAccess,
        documents: AuditDocumentRepository,
    ) -> None:
        """Права доступа и документы."""

        self.access = access
        self.documents = documents

    async def execute(
        self,
        *,
        audit_id: int,
        user: User,
    ) -> list[AuditDocumentResponse]:
        """Получить документы."""

        await self.access.get_visible(
            audit_id=audit_id,
            user=user,
        )
        documents = await self.documents.list_for_audit(audit_id=audit_id)

        return [AuditDocumentResponse.from_model(document=document) for document in documents]
