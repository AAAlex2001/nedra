"""Просмотр уведомлений."""

from src.notifications.repositories.notifications import NotificationRepository
from src.notifications.site.schemas.notification import NotificationResponse


class ListNotificationsUseCase:
    """Уведомления пользователя."""

    def __init__(self, *, notifications: NotificationRepository) -> None:
        """Репозиторий уведомлений."""

        self.notifications = notifications

    async def execute(
        self,
        *,
        user_id: int,
        limit: int,
    ) -> list[NotificationResponse]:
        """Получить последние уведомления."""

        notifications = await self.notifications.list_for_user(
            user_id=user_id,
            limit=limit,
        )

        return [
            NotificationResponse.from_model(notification=notification)
            for notification in notifications
        ]
