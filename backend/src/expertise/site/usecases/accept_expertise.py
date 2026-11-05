"""Принятие экспертизы исполнителем."""

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.contracts.enums import ContractKind
from src.contracts.models.contract import Contract
from src.contracts.repositories.contracts import ContractRepository
from src.expertise.application_validation import determine_contract_kind
from src.expertise.enums import ExpertiseStatus
from src.expertise.exceptions import (
    ExpertiseAccessError,
    ExpertiseNotFoundError,
    ExpertiseStateError,
    InvalidExpertiseError,
)
from src.expertise.expert_qualification import expert_qualifies
from src.expertise.repositories.expertises import ExpertiseRepository
from src.expertise.schemas.expertise import ExpertiseResponse
from src.expertise.site.expertise_letters import ExpertiseLetters
from src.notifications.models.notification import Notification
from src.notifications.repositories.notifications import NotificationRepository
from src.users.enums import UserRole
from src.users.exceptions import UserNotFoundError
from src.users.models.user import User
from src.users.repositories.expert_certificates import ExpertCertificateRepository
from src.users.repositories.users import UserRepository


class AcceptExpertiseUseCase:
    """Согласие с условиями заказчика."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        expertises: ExpertiseRepository,
        certificates: ExpertCertificateRepository,
        contracts: ContractRepository,
        users: UserRepository,
        notifications: NotificationRepository,
        letters: ExpertiseLetters,
    ) -> None:
        """Услуга, участники и уведомления."""

        self.session = session
        self.expertises = expertises
        self.certificates = certificates
        self.contracts = contracts
        self.users = users
        self.notifications = notifications
        self.letters = letters

    async def execute(
        self,
        *,
        expertise_id: int,
        user: User,
        contract_kind: ContractKind | None = None,
    ) -> ExpertiseResponse:
        """Принять работу на условиях заказчика."""

        if user.role != UserRole.EXPERT:
            raise ExpertiseAccessError("Работу принимает эксперт")

        expertise = await self.expertises.get_for_update(expertise_id=expertise_id)

        if expertise is None:
            raise ExpertiseNotFoundError()

        if expertise.status != ExpertiseStatus.NEW or expertise.expert_id is not None:
            raise ExpertiseStateError("Заявку уже взял другой исполнитель")

        certificates = await self.certificates.list_for_user(user_id=user.id)

        if not expert_qualifies(
            expertise=expertise,
            certificates=certificates,
        ):
            raise ExpertiseAccessError("Ваша аттестация не подходит под эту заявку")

        if expertise.price is None:
            raise ExpertiseStateError("В заявке нет цены")

        contract = await self.contracts.get_for_expertise(expertise_id=expertise_id)

        if contract is None:
            contract = Contract(expertise_id=expertise_id)

        if contract.kind is None:
            contract.kind = determine_contract_kind(
                object_code=expertise.object_code,
                chosen_kind=contract_kind,
            )

        if contract.kind is None:
            raise InvalidExpertiseError("Выберите вид договора по проекту заказчика")

        await self.contracts.save(contract=contract)
        expertise.expert_id = user.id
        expertise.expert_ready_at = datetime.now(UTC)

        customer = await self.users.get_by_id(user_id=expertise.customer_id)

        if customer is None:
            raise UserNotFoundError()

        expertise.status = ExpertiseStatus.EXPERT_READY
        await self.expertises.save(expertise=expertise)
        await self.notifications.add(
            notification=Notification(
                user_id=customer.id,
                expertise_id=expertise_id,
                text=f"Исполнитель готов выполнить экспертизу №{expertise_id}",
            )
        )
        response = ExpertiseResponse.from_model(expertise=expertise)
        await self.session.commit()
        await self.letters.send_expert_ready(
            expertise_id=expertise_id,
            recipient=customer.email,
            expert_name=user.full_name,
        )

        return response
