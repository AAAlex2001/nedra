"""Согласие заказчика с договором."""

import asyncio
from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.contracts.contract_documents import create_contract_document
from src.contracts.contract_files import ContractFiles
from src.contracts.repositories.contracts import ContractRepository
from src.core.settings import Settings
from src.expertise.enums import ExpertiseStatus
from src.expertise.exceptions import ExpertiseNotFoundError, ExpertiseStateError
from src.expertise.models.expertise_document import ExpertiseDocument
from src.expertise.repositories.expertise_contract_details import (
    ExpertiseContractDetailsRepository,
)
from src.expertise.repositories.expertise_documents import ExpertiseDocumentRepository
from src.expertise.repositories.expertises import ExpertiseRepository
from src.expertise.schemas.expertise import ExpertiseResponse
from src.notifications.models.notification import Notification
from src.notifications.repositories.notifications import NotificationRepository
from src.users.enums import UserRole
from src.users.models.user import User


class ConfirmExpertiseContractUseCase:
    """Подтверждение договора и соглашения."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        expertises: ExpertiseRepository,
        details: ExpertiseContractDetailsRepository,
        documents: ExpertiseDocumentRepository,
        contracts: ContractRepository,
        notifications: NotificationRepository,
        files: ContractFiles,
        settings: Settings,
    ) -> None:
        """Договор, файлы и участники."""

        self.session = session
        self.expertises = expertises
        self.details = details
        self.documents = documents
        self.contracts = contracts
        self.notifications = notifications
        self.files = files
        self.settings = settings

    async def execute(
        self,
        *,
        expertise_id: int,
        user: User,
    ) -> ExpertiseResponse:
        """Сохранить подписанные документы."""

        expertise = await self.expertises.get_for_update(expertise_id=expertise_id)

        if expertise is None or expertise.customer_id != user.id or user.role != UserRole.CUSTOMER:
            raise ExpertiseNotFoundError()

        if expertise.status != ExpertiseStatus.EXPERT_READY or expertise.expert_id is None:
            raise ExpertiseStateError("Исполнитель ещё не подтвердил готовность")

        details = await self.details.get(expertise_id=expertise_id)
        if details is None:
            raise ExpertiseNotFoundError()

        signed_at = datetime.now(UTC)
        terms = details.to_contract_terms(
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
                ExpertiseDocument(
                    expertise_id=expertise_id,
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
            expertise.status = ExpertiseStatus.CONTRACT
            await self.expertises.save(expertise=expertise)
            await self.notifications.add(
                notification=Notification(
                    user_id=expertise.expert_id,
                    expertise_id=expertise_id,
                    text=f"Заказчик подписал договор №{terms.number}, ожидается аванс",
                ),
            )
            response = ExpertiseResponse.from_model(expertise=expertise)
        except Exception:
            try:
                await self.session.rollback()
            finally:
                await self.files.remove_all(files=saved_files)

            raise

        try:
            await self.session.commit()
        except IntegrityError:
            try:
                await self.session.rollback()
            finally:
                await self.files.remove_all(files=saved_files)

            raise

        return response
