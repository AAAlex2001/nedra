"""Репозиторий уведомлений: только запросы к таблице notifications."""

from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


class NotificationRepository:
    """Доступ к таблице notifications. Сессию получает снаружи."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_for_user(self, user_id: int, limit: int) -> list[Notification]:
        """Последние уведомления пользователя, новые первыми."""

        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)

        return list(result.scalars().all())

    async def get_for_user(self, notification_id: int, user_id: int) -> Notification | None:
        """Уведомление по id, только если принадлежит пользователю."""

        stmt = select(Notification).where(
            Notification.id == notification_id, Notification.user_id == user_id
        )
        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    def add_all(self, notifications: list[Notification]) -> None:
        """Добавить пачку уведомлений в сессию. Без commit: коммитит вызывающий сценарий."""

        self.db.add_all(notifications)

    async def mark_read(self, notification: Notification) -> Notification:
        """Отметить прочитанным."""

        notification.read_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(notification)

        return notification

    async def mark_all_read(self, user_id: int) -> None:
        """Отметить прочитанными все непрочитанные уведомления пользователя."""

        stmt = (
            update(Notification)
            .where(Notification.user_id == user_id, Notification.read_at.is_(None))
            .values(read_at=datetime.now(timezone.utc))
        )
        await self.db.execute(stmt)
        await self.db.commit()
