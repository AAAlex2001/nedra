"""Открытие карточки экспертизы."""

from src.expertise.exceptions import ExpertiseNotFoundError
from src.expertise.repositories.expertises import ExpertiseRepository
from src.expertise.schemas.expertise import ExpertiseResponse


class GetAdminExpertiseUseCase:
    """Карточка для администратора."""

    def __init__(self, *, expertises: ExpertiseRepository) -> None:
        """Заявки на экспертизу."""

        self.expertises = expertises

    async def execute(self, *, expertise_id: int) -> ExpertiseResponse:
        """Открыть карточку."""

        expertise = await self.expertises.get_by_id(expertise_id=expertise_id)

        if expertise is None:
            raise ExpertiseNotFoundError()

        return ExpertiseResponse.from_model(expertise=expertise)
