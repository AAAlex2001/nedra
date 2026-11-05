"""Изменение экспертизы администратором."""

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.contracts.models.contract import Contract
from src.contracts.repositories.contracts import ContractRepository
from src.expertise.admin.schemas.expertise import UpdateExpertiseRequest
from src.expertise.application_validation import determine_contract_kind
from src.expertise.enums import ExpertiseStatus
from src.expertise.exceptions import ExpertiseNotFoundError, InvalidExpertiseError
from src.expertise.repositories.expertises import ExpertiseRepository
from src.users.enums import UserRole
from src.users.repositories.users import UserRepository


class UpdateExpertiseUseCase:
    """Изменение этапа, стоимости и исполнителя."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        expertises: ExpertiseRepository,
        contracts: ContractRepository,
        users: UserRepository,
    ) -> None:
        """Экспертизы, договоры и участники."""

        self.session = session
        self.expertises = expertises
        self.contracts = contracts
        self.users = users

    async def execute(
        self,
        *,
        expertise_id: int,
        payload: UpdateExpertiseRequest,
    ) -> None:
        """Сохранить изменения администратора."""

        expertise = await self.expertises.get_for_update(expertise_id=expertise_id)
        if expertise is None:
            raise ExpertiseNotFoundError()

        if payload.expert_id is not None:
            expert = await self.users.get_by_id(user_id=payload.expert_id)
            if expert is None or expert.role != UserRole.EXPERT:
                raise InvalidExpertiseError("Такого эксперта нет")

        if payload.status != ExpertiseStatus.NEW and payload.expert_id is None:
            raise InvalidExpertiseError("Для этого статуса нужен назначенный эксперт")

        contract = await self.contracts.get_for_expertise(expertise_id=expertise_id)
        if contract is None:
            contract = Contract(expertise_id=expertise_id)

        chosen_kind = payload.contract_kind or contract.kind
        if payload.expert_id is not None or payload.contract_kind is not None:
            contract.kind = determine_contract_kind(
                object_code=expertise.object_code,
                chosen_kind=chosen_kind,
            )

        if payload.expert_id is not None and contract.kind is None:
            raise InvalidExpertiseError("Выберите вид договора")

        if payload.expert_id is not None and expertise.expert_ready_at is None:
            expertise.expert_ready_at = datetime.now(UTC)

        expertise.expert_id = payload.expert_id
        expertise.status = payload.status
        expertise.price = payload.price
        await self.contracts.save(contract=contract)
        await self.expertises.save(expertise=expertise)
        await self.session.commit()
