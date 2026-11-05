"""Реквизиты заказчика экспертизы."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.expertise.models.expertise_company import ExpertiseCompany
from src.expertise.models.expertise_individual import ExpertiseIndividual


class ExpertiseCustomerRepository:
    """Чтение сохранённых реквизитов."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def get_company(self, *, expertise_id: int) -> ExpertiseCompany | None:
        """Получить реквизиты организации или ИП."""

        return await self.session.get(ExpertiseCompany, expertise_id)

    async def get_individual(self, *, expertise_id: int) -> ExpertiseIndividual | None:
        """Получить реквизиты физлица."""

        return await self.session.get(ExpertiseIndividual, expertise_id)
