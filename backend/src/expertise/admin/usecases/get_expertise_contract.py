"""Просмотр условий договора."""

from src.contracts.repositories.contracts import ContractRepository
from src.expertise.exceptions import ExpertiseNotFoundError
from src.expertise.repositories.expertises import ExpertiseRepository
from src.expertise.schemas.expertise_contract import ExpertiseContractResponse


class GetAdminExpertiseContractUseCase:
    """Вид и подтверждение договора."""

    def __init__(
        self,
        *,
        expertises: ExpertiseRepository,
        contracts: ContractRepository,
    ) -> None:
        """Права доступа и договоры."""

        self.expertises = expertises
        self.contracts = contracts

    async def execute(self, *, expertise_id: int) -> ExpertiseContractResponse | None:
        """Получить сведения о договоре."""

        expertise = await self.expertises.get_by_id(expertise_id=expertise_id)

        if expertise is None:
            raise ExpertiseNotFoundError()

        contract = await self.contracts.get_for_expertise(expertise_id=expertise_id)

        if contract is None:
            return None

        return ExpertiseContractResponse.from_model(contract=contract)
