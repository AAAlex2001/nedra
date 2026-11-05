"""Запросы на смену почты."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models.email_change import EmailChange


class EmailChangeRepository:
    """Коды подтверждения новой почты."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def get_by_user_id(self, *, user_id: int) -> EmailChange | None:
        """Найти запрос пользователя."""

        return await self.session.get(EmailChange, user_id)

    async def save(self, *, email_change: EmailChange) -> None:
        """Сохранить запрос."""

        self.session.add(email_change)
        await self.session.flush()

    async def remove(self, *, email_change: EmailChange) -> None:
        """Удалить использованный запрос."""

        await self.session.delete(email_change)
        await self.session.flush()
