"""Эксперт сам меняет направления работы в личном кабинете."""

from app.models.expert import ExpertProfile
from app.services.experts.exceptions import ExpertNotFoundError
from app.services.experts.repo import ExpertApplicationRepository, ExpertProfileRepository
from app.services.experts.validators import validate_directions


class UpdateDirectionsUseCase:
    """Поменять направления работы.

    От направлений зависит, какие заявки видит эксперт: с «Аудит СУПБ» он
    получает заявки на аудит. Список дублируется в заявке эксперта — правим обе.
    """

    def __init__(
        self, profiles: ExpertProfileRepository, applications: ExpertApplicationRepository
    ) -> None:
        self.profiles = profiles
        self.applications = applications

    async def execute(self, user_id: int, directions: list[str]) -> ExpertProfile:
        """Бросает ExpertNotFoundError, InvalidDirectionError."""

        profile = await self.profiles.get_by_user(user_id)
        if profile is None:
            raise ExpertNotFoundError(f"Эксперт {user_id} не найден")

        validate_directions(directions)
        profile.directions = directions

        application = await self.applications.get_by_user_id(user_id)
        if application is not None:
            application.directions = directions

        await self.profiles.save()

        return profile
