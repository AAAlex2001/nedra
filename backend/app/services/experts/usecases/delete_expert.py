"""Сценарий удаления эксперта администратором."""

from datetime import datetime, timezone

from app.models.expert import ApplicationStatus
from app.services.experts.exceptions import ExpertNotFoundError
from app.services.experts.repo import ExpertApplicationRepository, ExpertProfileRepository
from app.services.users.repo import UserRepository

DELETED_COMMENT = "Профиль эксперта удалён администратором"


class DeleteExpertUseCase:
    """Убрать профиль эксперта, удостоверения и сам аккаунт.

    Аккаунт эксперта нужен только для работы по заявкам, поэтому без профиля
    он не нужен. Заявка остаётся в истории как отклонённая с пометкой.
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
        """Снять профиль и удалить аккаунт. Бросает ExpertNotFoundError."""

        user = await self.users.get_by_id(user_id)
        profile = await self.profiles.get_by_user(user_id)
        if user is None or profile is None:
            raise ExpertNotFoundError(f"Эксперт {user_id} не найден")

        application = await self.applications.get_by_user_id(user_id)
        if application is not None:
            application.status = ApplicationStatus.REJECTED
            application.admin_comment = DELETED_COMMENT
            application.reviewed_at = datetime.now(timezone.utc)
            application.user_id = None

        await self.profiles.remove(profile)
        await self.users.delete(user)
