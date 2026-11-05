"""Чтение данных для договора экспертизы."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.contracts.models.contract import Contract
from src.expertise.expertise_contract_details import ExpertiseContractDetails
from src.expertise.models.expertise import Expertise
from src.expertise.models.expertise_company import ExpertiseCompany
from src.expertise.models.expertise_individual import ExpertiseIndividual


class ExpertiseContractDetailsRepository:
    """Условия и реквизиты договора."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def get(self, *, expertise_id: int) -> ExpertiseContractDetails | None:
        """Получить данные для договора."""

        expertise = await self.session.get(Expertise, expertise_id)
        if expertise is None:
            return None

        contract_statement = select(Contract).where(Contract.expertise_id == expertise_id)
        contract = await self.session.scalar(contract_statement)
        company = await self.session.get(ExpertiseCompany, expertise_id)
        individual = await self.session.get(ExpertiseIndividual, expertise_id)

        return ExpertiseContractDetails(
            expertise=expertise,
            contract=contract,
            company=company,
            individual=individual,
        )
