"""Прочтение всех уведомлений."""

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.notifications.options import DEFAULT_LIST_LIMIT
from src.notifications.repositories.notifications import NotificationRepository
from src.notifications.site.schemas.notification import NotificationResponse


class ReadAllNotificationsUseCase:
    """Отметка всех уведомлений прочитанными."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        notifications: NotificationRepository,
    ) -> None:
        """Сессия и уведомления."""

        self.session = session
        self.notifications = notifications

    async def execute(self, *, user_id: int) -> list[NotificationResponse]:
        """Прочитать все уведомления пользователя."""

        await self.notifications.mark_all_read(
            user_id=user_id,
            read_at=datetime.now(UTC),
        )
        notifications = await self.notifications.list_for_user(
            user_id=user_id,
            limit=DEFAULT_LIST_LIMIT,
        )
        response = [
            NotificationResponse.from_model(notification=notification)
            for notification in notifications
        ]
        await self.session.commit()

        return response
