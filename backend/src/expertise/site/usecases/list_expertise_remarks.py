"""Просмотр замечаний эксперта."""

from src.expertise.repositories.expertise_documents import ExpertiseDocumentRepository
from src.expertise.repositories.expertise_remarks import ExpertiseRemarkRepository
from src.expertise.site.expertise_access import ExpertiseAccess
from src.expertise.site.schemas.expertise_documents import (
    ExpertiseDocumentResponse,
    ExpertiseRemarkResponse,
)
from src.users.models.user import User


class ListExpertiseRemarksUseCase:
    """Замечания и приложенные файлы."""

    def __init__(
        self,
        *,
        access: ExpertiseAccess,
        remarks: ExpertiseRemarkRepository,
        documents: ExpertiseDocumentRepository,
    ) -> None:
        """Права доступа, замечания и файлы."""

        self.access = access
        self.remarks = remarks
        self.documents = documents

    async def execute(
        self,
        *,
        expertise_id: int,
        user: User,
    ) -> list[ExpertiseRemarkResponse]:
        """Получить замечания с приложениями."""

        await self.access.get_visible(
            expertise_id=expertise_id,
            user=user,
        )
        remarks = await self.remarks.list_for_expertise(expertise_id=expertise_id)
        documents = await self.documents.list_for_remarks(expertise_id=expertise_id)
        documents_by_remark_id: dict[int, list[ExpertiseDocumentResponse]] = {}

        for document in documents:
            if document.remark_id not in documents_by_remark_id:
                documents_by_remark_id[document.remark_id] = []

            documents_by_remark_id[document.remark_id].append(
                ExpertiseDocumentResponse.from_model(document=document),
            )

        return [
            ExpertiseRemarkResponse.from_model(
                remark=remark,
                documents=documents_by_remark_id.get(remark.id, []),
            )
            for remark in remarks
        ]
