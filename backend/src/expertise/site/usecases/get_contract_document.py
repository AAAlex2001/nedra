"""Скачивание договора или соглашения."""

import asyncio
from datetime import UTC, datetime
from typing import Literal

from src.contracts.contract_documents import create_contract_document
from src.core.file_exceptions import InvalidUploadError
from src.core.file_storage import FileStorage
from src.core.settings import Settings
from src.documents.generated_document import GeneratedDocument
from src.expertise.exceptions import (
    ExpertiseDocumentNotFoundError,
    ExpertiseNotFoundError,
)
from src.expertise.repositories.expertise_contract_details import (
    ExpertiseContractDetailsRepository,
)
from src.expertise.repositories.expertise_documents import ExpertiseDocumentRepository
from src.expertise.site.expertise_access import ExpertiseAccess
from src.users.exceptions import UserNotFoundError
from src.users.models.user import User
from src.users.repositories.users import UserRepository


class GetExpertiseContractDocumentUseCase:
    """Проект договора или сохранённый экземпляр."""

    def __init__(
        self,
        *,
        access: ExpertiseAccess,
        details: ExpertiseContractDetailsRepository,
        users: UserRepository,
        documents: ExpertiseDocumentRepository,
        storage: FileStorage,
        settings: Settings,
    ) -> None:
        """Доступ, реквизиты и файлы."""

        self.access = access
        self.details = details
        self.users = users
        self.documents = documents
        self.storage = storage
        self.settings = settings

    async def execute(
        self,
        *,
        expertise_id: int,
        document_kind: Literal["contract", "nda"],
        user: User,
    ) -> GeneratedDocument:
        """Получить документ для ознакомления."""

        expertise = await self.access.get_visible(
            expertise_id=expertise_id,
            user=user,
        )
        document = await self.documents.get_latest_by_kind(
            expertise_id=expertise_id,
            kind=document_kind,
        )

        if document is not None:
            try:
                path = self.storage.resolve_path(relative_path=document.file_path)
                content = await asyncio.to_thread(path.read_bytes)
            except (InvalidUploadError, FileNotFoundError) as error:
                raise ExpertiseDocumentNotFoundError() from error

            return GeneratedDocument(
                content=content,
                filename=document.original_name,
                content_type=document.content_type,
            )

        customer = await self.users.get_by_id(user_id=expertise.customer_id)

        if customer is None:
            raise UserNotFoundError()

        details = await self.details.get(expertise_id=expertise_id)

        if details is None:
            raise ExpertiseNotFoundError()

        terms = details.to_contract_terms(
            customer=customer,
            signed_at=datetime.now(UTC),
            settings=self.settings,
        )
        document = await asyncio.to_thread(
            create_contract_document,
            document_kind=document_kind,
            terms=terms,
        )

        return GeneratedDocument(
            content=document.content,
            filename=f"Проект — {document.filename}",
            content_type=document.content_type,
        )
