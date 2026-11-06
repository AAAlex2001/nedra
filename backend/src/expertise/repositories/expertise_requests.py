"""Сохранение заявки и её приложений."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.expertise.models.expertise import Expertise
from src.expertise.models.expertise_company import ExpertiseCompany
from src.expertise.models.expertise_document import ExpertiseDocument
from src.expertise.models.expertise_individual import ExpertiseIndividual


class ExpertiseRequestRepository:
    """Записи одной заявки."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def add(
        self,
        *,
        expertise: Expertise,
        company: ExpertiseCompany | None,
        individual: ExpertiseIndividual | None,
        documents: list[ExpertiseDocument],
    ) -> None:
        """Добавить заявку, реквизиты и документы."""

        self.session.add(expertise)
        await self.session.flush()

        if company is not None:
            company.expertise_id = expertise.id
            self.session.add(company)

        if individual is not None:
            individual.expertise_id = expertise.id
            self.session.add(individual)

        for document in documents:
            document.expertise_id = expertise.id

        self.session.add_all(documents)
        await self.session.flush()
