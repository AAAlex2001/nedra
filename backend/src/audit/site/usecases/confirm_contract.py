"""Согласие заказчика с договором."""

import asyncio
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.enums import AuditStatus
from src.audit.exceptions import AuditNotFoundError, AuditStateError
from src.audit.models.audit_document import AuditDocument
from src.audit.repositories.audit_contract_details import AuditContractDetailsRepository
from src.audit.repositories.audit_documents import AuditDocumentRepository
from src.audit.repositories.audits import AuditRepository
from src.audit.schemas.audit import AuditResponse
from src.audit.site.audit_contract import prepare_audit_contract
from src.contracts.contract_documents import create_contract_document
from src.contracts.contract_files import ContractFiles
from src.contracts.repositories.contracts import ContractRepository
from src.core.settings import Settings
from src.notifications.models.notification import Notification
from src.notifications.repositories.notifications import NotificationRepository
from src.users.enums import UserRole
from src.users.models.user import User


class ConfirmAuditContractUseCase:
    """Подтверждение договора и соглашения."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        audits: AuditRepository,
        details: AuditContractDetailsRepository,
        documents: AuditDocumentRepository,
        contracts: ContractRepository,
        notifications: NotificationRepository,
        files: ContractFiles,
        settings: Settings,
    ) -> None:
        """Договор, файлы и участники."""

        self.session = session
        self.audits = audits
        self.details = details
        self.documents = documents
        self.contracts = contracts
        self.notifications = notifications
        self.files = files
        self.settings = settings

    async def execute(
        self,
        *,
        audit_id: int,
        user: User,
    ) -> AuditResponse:
        """Сохранить подписанные документы."""

        audit = await self.audits.get_for_update(audit_id=audit_id)

        if audit is None or audit.customer_id != user.id or user.role != UserRole.CUSTOMER:
            raise AuditNotFoundError()

        if audit.status != AuditStatus.EXPERT_READY or audit.lead_id is None:
            raise AuditStateError("Исполнитель ещё не подтвердил готовность")

        details = await self.details.get(audit_id=audit_id)
        if details is None:
            raise AuditNotFoundError()

        signed_at = datetime.now(UTC)
        terms = prepare_audit_contract(
            details=details,
            customer=user,
            signed_at=signed_at,
            settings=self.settings,
        )
        generated_documents = {}

        for kind in ("contract", "nda"):
            generated_documents[kind] = await asyncio.to_thread(
                create_contract_document,
                document_kind=kind,
                terms=terms,
            )

        saved_files = await self.files.save_all(documents=generated_documents)

        try:
            documents = [
                AuditDocument(
                    audit_id=audit_id,
                    uploaded_by=user.id,
                    kind=kind,
                    file_path=stored_file.path,
                    original_name=stored_file.original_name,
                    size=stored_file.size,
                    content_type=stored_file.content_type,
                )
                for kind, stored_file in saved_files.items()
            ]
            await self.documents.add_many(documents=documents)
            details.contract.confirmed_at = signed_at
            await self.contracts.save(contract=details.contract)
            audit.status = AuditStatus.CONTRACT
            await self.audits.save(audit=audit)
            await self.notifications.add(
                notification=Notification(
                    user_id=audit.lead_id,
                    audit_id=audit_id,
                    text=f"Заказчик подписал договор №{terms.number}, ожидается аванс",
                ),
            )
            response = AuditResponse.from_model(audit=audit)
        except Exception:
            try:
                await self.session.rollback()
            finally:
                await self.files.remove_all(files=saved_files)

            raise

        await self.session.commit()

        return response
