"""Сценарий снятия роли эксперта администратором."""

from datetime import datetime, timezone

from app.models.expert import ApplicationStatus
from app.models.user import UserRole
from app.services.experts.exceptions import ExpertNotFoundError
from app.services.experts.repo import ExpertApplicationRepository, ExpertProfileRepository
from app.services.users.repo import UserRepository

DELETED_COMMENT = "Профиль эксперта удалён администратором"


class DeleteExpertUseCase:
    """Убрать у аккаунта профиль эксперта и удостоверения, оставив его заказчиком.

    Сам аккаунт не удаляем: у человека может быть роль заказчика с заявками.
    Его заявка эксперта остаётся в истории как отклонённая с пометкой.
    """

    def __init__(
        self,
        users: UserRepository,
        applications: ExpertApplicationRepository,
        profiles: ExpertProfileRepository,
    ) -> None:
        self.users = users
        self.applications = applications
        self.profiles = profiles

    async def execute(self, user_id: int) -> None:
        """Снять роль эксперта. Бросает ExpertNotFoundError."""

        user = await self.users.get_by_id(user_id)
        profile = await self.profiles.get_by_user(user_id)
        if user is None or profile is None:
            raise ExpertNotFoundError(f"Эксперт {user_id} не найден")

        application = await self.applications.get_by_user_id(user_id)
        if application is not None:
            application.status = ApplicationStatus.REJECTED
            application.admin_comment = DELETED_COMMENT
            application.reviewed_at = datetime.now(timezone.utc)

        user.role = UserRole.CUSTOMER

        await self.profiles.remove(profile)
