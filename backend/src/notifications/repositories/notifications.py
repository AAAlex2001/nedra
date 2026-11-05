"""Сохранение уведомлений."""

from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.notifications.models.notification import Notification


class NotificationRepository:
    """Уведомления пользователей."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def add(self, *, notification: Notification) -> None:
        """Добавить уведомление."""

        self.session.add(notification)
        await self.session.flush()

    async def list_for_user(
        self,
        *,
        user_id: int,
        limit: int,
    ) -> list[Notification]:
        """Получить последние уведомления пользователя."""

        statement = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(
                Notification.created_at.desc(),
                Notification.id.desc(),
            )
            .limit(limit)
        )
        query_result = await self.session.scalars(statement)

        return list(query_result)

    async def get_for_user(
        self,
        *,
        notification_id: int,
        user_id: int,
    ) -> Notification | None:
        """Найти уведомление пользователя."""

        statement = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
        query_result = await self.session.scalars(statement)

        return query_result.one_or_none()

    async def mark_read(
        self,
        *,
        notification_id: int,
        user_id: int,
        read_at: datetime,
    ) -> None:
        """Отметить уведомление прочитанным."""

        statement = (
            update(Notification)
            .where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
                Notification.read_at.is_(None),
            )
            .values(read_at=read_at)
        )
        await self.session.execute(statement)

    async def mark_all_read(
        self,
        *,
        user_id: int,
        read_at: datetime,
    ) -> None:
        """Отметить все уведомления прочитанными."""

        statement = (
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.read_at.is_(None),
            )
            .values(read_at=read_at)
        )
        await self.session.execute(statement)

    async def add_many(self, *, notifications: list[Notification]) -> None:
        """Добавить уведомления."""

        self.session.add_all(notifications)
        await self.session.flush()
