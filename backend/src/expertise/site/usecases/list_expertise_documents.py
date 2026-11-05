"""Просмотр документов экспертизы."""

from src.expertise.repositories.expertise_documents import ExpertiseDocumentRepository
from src.expertise.site.expertise_access import ExpertiseAccess
from src.expertise.site.schemas.expertise_documents import ExpertiseDocumentResponse
from src.users.models.user import User


class ListExpertiseDocumentsUseCase:
    """Список файлов экспертизы."""

    def __init__(
        self,
        *,
        access: ExpertiseAccess,
        documents: ExpertiseDocumentRepository,
    ) -> None:
        """Права доступа и документы."""

        self.access = access
        self.documents = documents

    async def execute(
        self,
        *,
        expertise_id: int,
        user: User,
    ) -> list[ExpertiseDocumentResponse]:
        """Получить документы."""

        await self.access.get_visible(
            expertise_id=expertise_id,
            user=user,
        )
        documents = await self.documents.list_for_expertise(expertise_id=expertise_id)

        return [ExpertiseDocumentResponse.from_model(document=document) for document in documents]
