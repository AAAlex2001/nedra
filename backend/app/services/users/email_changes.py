"""Репозиторий запросов на смену email: только запросы к таблице email_changes."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.email_change import EmailChange


class EmailChangeRepository:
    """Доступ к таблице email_changes. Коммит делает UserRepository той же сессии."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get(self, user_id: int) -> EmailChange | None:
        """Активный запрос пользователя или None."""

        return await self.db.get(EmailChange, user_id)

    async def put(self, change: EmailChange) -> None:
        """Записать запрос, заменив прежний."""

        await self.db.merge(change)
        await self.db.commit()

    async def remove(self, change: EmailChange) -> None:
        """Удалить запрос. Коммит — вместе с сохранением пользователя."""

        await self.db.delete(change)
