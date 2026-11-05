"""Просмотр условий договора."""

from src.contracts.repositories.contracts import ContractRepository
from src.expertise.schemas.expertise_contract import ExpertiseContractResponse
from src.expertise.site.expertise_access import ExpertiseAccess
from src.users.models.user import User


class GetExpertiseContractUseCase:
    """Вид и подтверждение договора."""

    def __init__(
        self,
        *,
        access: ExpertiseAccess,
        contracts: ContractRepository,
    ) -> None:
        """Права доступа и договоры."""

        self.access = access
        self.contracts = contracts

    async def execute(
        self,
        *,
        expertise_id: int,
        user: User,
    ) -> ExpertiseContractResponse | None:
        """Получить сведения о договоре."""

        await self.access.get_visible(
            expertise_id=expertise_id,
            user=user,
        )
        contract = await self.contracts.get_for_expertise(expertise_id=expertise_id)

        if contract is None:
            return None

        return ExpertiseContractResponse.from_model(contract=contract)
