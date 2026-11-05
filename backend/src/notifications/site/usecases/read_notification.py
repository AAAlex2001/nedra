"""Прочтение уведомления."""

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.notifications.exceptions import NotificationNotFoundError
from src.notifications.repositories.notifications import NotificationRepository
from src.notifications.site.schemas.notification import NotificationResponse


class ReadNotificationUseCase:
    """Отметка о прочтении уведомления."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        notifications: NotificationRepository,
    ) -> None:
        """Сессия и уведомления."""

        self.session = session
        self.notifications = notifications

    async def execute(
        self,
        *,
        notification_id: int,
        user_id: int,
    ) -> NotificationResponse:
        """Отметить уведомление прочитанным."""

        await self.notifications.mark_read(
            notification_id=notification_id,
            user_id=user_id,
            read_at=datetime.now(UTC),
        )
        notification = await self.notifications.get_for_user(
            notification_id=notification_id,
            user_id=user_id,
        )

        if notification is None:
            raise NotificationNotFoundError()

        response = NotificationResponse.from_model(notification=notification)
        await self.session.commit()

        return response
