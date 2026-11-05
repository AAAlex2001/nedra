"""Подача документации на экспертизу."""

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.contracts.models.contract import Contract
from src.contracts.repositories.contracts import ContractRepository
from src.expertise.application_validation import (
    determine_contract_kind,
    determine_expert_category,
    validate_expertise_codes,
)
from src.expertise.exceptions import ExpertiseAccessError, InvalidExpertiseError
from src.expertise.repositories.expertise_requests import ExpertiseRequestRepository
from src.expertise.repositories.qualified_experts import QualifiedExpertRepository
from src.expertise.schemas.expertise import ExpertiseResponse
from src.expertise.site.expertise_file_storage import ExpertiseAttachment, ExpertiseFileStorage
from src.expertise.site.expertise_letters import ExpertiseLetters
from src.expertise.site.schemas.create_expertise import CreateExpertiseRequest
from src.notifications.models.notification import Notification
from src.notifications.repositories.notifications import NotificationRepository
from src.users.enums import UserRole
from src.users.models.user import User


class CreateExpertiseUseCase:
    """Новая заявка на экспертизу."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        requests: ExpertiseRequestRepository,
        contracts: ContractRepository,
        experts: QualifiedExpertRepository,
        notifications: NotificationRepository,
        files: ExpertiseFileStorage,
        letters: ExpertiseLetters,
    ) -> None:
        """Заявки, исполнители и документы."""

        self.session = session
        self.requests = requests
        self.contracts = contracts
        self.experts = experts
        self.notifications = notifications
        self.files = files
        self.letters = letters

    async def execute(
        self,
        *,
        user: User,
        payload: CreateExpertiseRequest,
        files: list[UploadFile],
        company_card: UploadFile | None,
    ) -> ExpertiseResponse:
        """Подать заявку на экспертизу."""

        if user.role != UserRole.CUSTOMER:
            raise ExpertiseAccessError("Заявку подаёт заказчик")

        validate_expertise_codes(
            object_code=payload.object_code,
            area_code=payload.area_code,
        )
        category = determine_expert_category(
            hazard_class=payload.hazard_class,
            expert_category=payload.expert_category,
        )
        contract_kind = determine_contract_kind(
            object_code=payload.object_code,
            chosen_kind=payload.contract_kind,
        )

        if not files:
            raise InvalidExpertiseError("Приложите хотя бы один файл документации")

        attachments = [
            ExpertiseAttachment(
                file=file,
                kind="documentation",
            )
            for file in files
        ]

        if company_card is not None:
            attachments.append(
                ExpertiseAttachment(
                    file=company_card,
                    kind="company_card",
                )
            )

        experts = await self.experts.list_for_expertise(
            object_code=payload.object_code,
            area_code=payload.area_code,
            expert_category=category,
        )
        documents = await self.files.save_all(
            attachments=attachments,
        )

        try:
            expertise = await self.requests.create(
                customer_id=user.id,
                payload=payload,
                expert_category=category,
                documents=documents,
            )
            await self.contracts.save(
                contract=Contract(
                    expertise_id=expertise.id,
                    kind=contract_kind,
                ),
            )
            notifications = [
                Notification(
                    user_id=expert.id,
                    expertise_id=expertise.id,
                    text=f"Новая заявка на экспертизу №{expertise.id}",
                )
                for expert in experts
            ]
            await self.notifications.add_many(notifications=notifications)
            response = ExpertiseResponse.from_model(expertise=expertise)
        except Exception:
            try:
                await self.session.rollback()
            finally:
                await self.files.remove_all(documents=documents)

            raise

        await self.session.commit()
        await self.letters.send_new_request(
            expertise_id=response.id,
            object_name=payload.object_name,
            recipients=[expert.email for expert in experts],
        )

        return response
