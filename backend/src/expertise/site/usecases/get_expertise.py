"""Открытие карточки экспертизы."""

from src.expertise.schemas.expertise import ExpertiseResponse
from src.expertise.site.expertise_access import ExpertiseAccess
from src.users.models.user import User


class GetExpertiseUseCase:
    """Карточка для участника услуги."""

    def __init__(self, *, access: ExpertiseAccess) -> None:
        """Права доступа к экспертизе."""

        self.access = access

    async def execute(
        self,
        *,
        expertise_id: int,
        user: User,
    ) -> ExpertiseResponse:
        """Открыть карточку."""

        expertise = await self.access.get_visible(
            expertise_id=expertise_id,
            user=user,
        )
        return ExpertiseResponse.from_model(expertise=expertise)
