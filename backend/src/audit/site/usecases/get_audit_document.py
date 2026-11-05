"""Скачивание документа аудита."""

from pathlib import Path

from src.audit.exceptions import AuditDocumentNotFoundError
from src.audit.repositories.audit_documents import AuditDocumentRepository
from src.audit.site.audit_access import AuditAccess
from src.core.file_exceptions import InvalidUploadError
from src.core.file_storage import FileStorage
from src.users.models.user import User


class GetAuditDocumentUseCase:
    """Файл для участника услуги."""

    def __init__(
        self,
        *,
        access: AuditAccess,
        documents: AuditDocumentRepository,
        storage: FileStorage,
    ) -> None:
        """Права доступа, документы и хранилище."""

        self.access = access
        self.documents = documents
        self.storage = storage

    async def execute(
        self,
        *,
        audit_id: int,
        document_id: int,
        user: User,
    ) -> tuple[Path, str]:
        """Получить файл документа."""

        await self.access.get_visible(
            audit_id=audit_id,
            user=user,
        )
        document = await self.documents.get(
            audit_id=audit_id,
            document_id=document_id,
        )

        if document is None:
            raise AuditDocumentNotFoundError()

        try:
            path = self.storage.resolve_path(relative_path=document.file_path)
        except InvalidUploadError:
            raise AuditDocumentNotFoundError() from None

        if not path.is_file():
            raise AuditDocumentNotFoundError()

        return path, document.original_name
