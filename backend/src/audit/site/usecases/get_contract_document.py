"""Скачивание договора или соглашения."""

import asyncio
from datetime import UTC, datetime
from typing import Literal

from src.audit.exceptions import AuditDocumentNotFoundError, AuditNotFoundError
from src.audit.repositories.audit_contract_details import AuditContractDetailsRepository
from src.audit.repositories.audit_documents import AuditDocumentRepository
from src.audit.site.audit_access import AuditAccess
from src.audit.site.audit_contract import prepare_audit_contract
from src.contracts.contract_documents import create_contract_document
from src.core.file_exceptions import InvalidUploadError
from src.core.file_storage import FileStorage
from src.core.settings import Settings
from src.documents.generated_document import GeneratedDocument
from src.users.exceptions import UserNotFoundError
from src.users.models.user import User
from src.users.repositories.users import UserRepository


class GetAuditContractDocumentUseCase:
    """Проект договора или сохранённый экземпляр."""

    def __init__(
        self,
        *,
        access: AuditAccess,
        details: AuditContractDetailsRepository,
        users: UserRepository,
        documents: AuditDocumentRepository,
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
        audit_id: int,
        document_kind: Literal["contract", "nda"],
        user: User,
    ) -> GeneratedDocument:
        """Получить документ для ознакомления."""

        audit = await self.access.get_visible(
            audit_id=audit_id,
            user=user,
        )
        document = await self.documents.get_latest_by_kind(
            audit_id=audit_id,
            kind=document_kind,
        )

        if document is not None:
            try:
                path = self.storage.resolve_path(relative_path=document.file_path)
                content = await asyncio.to_thread(path.read_bytes)
            except (InvalidUploadError, FileNotFoundError) as error:
                raise AuditDocumentNotFoundError() from error

            return GeneratedDocument(
                content=content,
                filename=document.original_name,
                content_type=document.content_type,
            )

        customer = await self.users.get_by_id(user_id=audit.customer_id)

        if customer is None:
            raise UserNotFoundError()

        details = await self.details.get(audit_id=audit_id)

        if details is None:
            raise AuditNotFoundError()

        terms = prepare_audit_contract(
            details=details,
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
