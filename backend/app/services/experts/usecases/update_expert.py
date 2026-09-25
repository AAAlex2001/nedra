"""Правка данных эксперта из админки."""

from app.models.expert import ExpertProfile
from app.models.user import User
from app.schemas.expert import ExpertUpdateSchema
from app.services.experts.exceptions import ExpertNotFoundError
from app.services.experts.repo import ExpertApplicationRepository, ExpertProfileRepository
from app.services.experts.validators import validate_directions
from app.services.users.repo import UserRepository
from app.services.users.validators import normalize_phone


class UpdateExpertUseCase:
    """Поменять имя, телефон и направления эксперта.

    Направления дублируются в заявке, из которой создан профиль, поэтому
    правим обе записи: иначе в админке останется старый список.
    """

    def __init__(
        self,
        users: UserRepository,
        profiles: ExpertProfileRepository,
        applications: ExpertApplicationRepository,
    ) -> None:
        self.users = users
        self.profiles = profiles
        self.applications = applications

    async def execute(self, user_id: int, data: ExpertUpdateSchema) -> tuple[User, ExpertProfile]:
        """Бросает ExpertNotFoundError, InvalidDirectionError, InvalidPhoneError."""

        user = await self.users.get_by_id(user_id)
        profile = await self.profiles.get_by_user(user_id)
        if user is None or profile is None:
            raise ExpertNotFoundError(f"Эксперт {user_id} не найден")

        validate_directions(data.directions)

        user.full_name = data.full_name.strip()
        user.phone = normalize_phone(data.phone)
        profile.directions = data.directions

        application = await self.applications.get_by_user_id(user_id)
        if application is not None:
            application.full_name = user.full_name
            application.phone = user.phone
            application.directions = data.directions

        await self.profiles.save()

        return user, profile
