"""Сценарий переключения активной роли."""

from app.models.user import User, UserRole
from app.services.experts.repo import ExpertProfileRepository
from app.services.users.exceptions import RoleNotAvailableError
from app.services.users.repo import UserRepository


class SwitchRoleUseCase:
    """Сменить активную роль. Заказчиком может быть любой, экспертом — только с одобренным профилем."""

    def __init__(self, users: UserRepository, profiles: ExpertProfileRepository) -> None:
        self.users = users
        self.profiles = profiles

    async def execute(self, user: User, role: UserRole) -> User:
        """Переключить роль. Бросает RoleNotAvailableError."""

        if role == UserRole.EXPERT:
            profile = await self.profiles.get_by_user(user.id)
            if profile is None:
                raise RoleNotAvailableError("Роль эксперта доступна после одобрения заявки")

        user.role = role

        return await self.users.save(user)
