"""Сценарий удаления эксперта администратором."""

from datetime import datetime, timezone

from app.models.expert import ApplicationStatus
from app.models.user import UserRole
from app.services.experts.exceptions import ExpertNotFoundError
from app.services.experts.repo import ExpertApplicationRepository
from app.services.users.repo import UserRepository

DELETED_COMMENT = "Аккаунт эксперта удалён администратором"


class DeleteExpertUseCase:
    """Удалить пользователя-эксперта и пометить его заявку отклонённой.

    Профиль, удостоверения и уведомления удаляет база каскадом. Заявка остаётся
    в истории: по ней видно, что эксперт был и его удалили. Экспертизы,
    где он был назначен, теряют эксперта и возвращаются в общую очередь.
    """

    def __init__(self, users: UserRepository, applications: ExpertApplicationRepository) -> None:
        self.users = users
        self.applications = applications

    async def execute(self, user_id: int) -> None:
        """Удалить эксперта. Бросает ExpertNotFoundError."""

        user = await self.users.get_by_id(user_id)
        if user is None or user.role != UserRole.EXPERT:
            raise ExpertNotFoundError(f"Эксперт {user_id} не найден")

        application = await self.applications.get_by_user_id(user_id)
        if application is not None:
            application.status = ApplicationStatus.REJECTED
            application.admin_comment = DELETED_COMMENT
            application.reviewed_at = datetime.now(timezone.utc)
            application.user_id = None

        await self.users.delete(user)
