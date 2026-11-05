"""Скачивание документа экспертизы."""

from pathlib import Path

from src.core.file_exceptions import InvalidUploadError
from src.core.file_storage import FileStorage
from src.expertise.exceptions import ExpertiseDocumentNotFoundError
from src.expertise.repositories.expertise_documents import ExpertiseDocumentRepository
from src.expertise.site.expertise_access import ExpertiseAccess
from src.users.models.user import User


class GetExpertiseDocumentUseCase:
    """Файл для участника услуги."""

    def __init__(
        self,
        *,
        access: ExpertiseAccess,
        documents: ExpertiseDocumentRepository,
        storage: FileStorage,
    ) -> None:
        """Права доступа, документы и хранилище."""

        self.access = access
        self.documents = documents
        self.storage = storage

    async def execute(
        self,
        *,
        expertise_id: int,
        document_id: int,
        user: User,
    ) -> tuple[Path, str]:
        """Получить файл документа."""

        await self.access.get_visible(
            expertise_id=expertise_id,
            user=user,
        )
        document = await self.documents.get(
            expertise_id=expertise_id,
            document_id=document_id,
        )

        if document is None:
            raise ExpertiseDocumentNotFoundError()

        try:
            path = self.storage.resolve_path(relative_path=document.file_path)
        except InvalidUploadError:
            raise ExpertiseDocumentNotFoundError() from None

        if not path.is_file():
            raise ExpertiseDocumentNotFoundError()

        return path, document.original_name
