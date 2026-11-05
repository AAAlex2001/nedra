"""Учётные записи пользователей."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.enums import UserRole
from src.users.models.user import User


class UserRepository:
    """Поиск и сохранение пользователей."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def get_by_id(self, *, user_id: int) -> User | None:
        """Найти пользователя по номеру."""

        return await self.session.get(User, user_id)

    async def get_by_email(self, *, email: str) -> User | None:
        """Найти пользователя по почте."""

        statement = select(User).where(User.email == email)
        query_result = await self.session.scalars(statement)

        return query_result.one_or_none()

    async def list_by_role(self, *, role: UserRole) -> list[User]:
        """Получить аккаунты выбранной роли."""

        statement = (
            select(User).where(User.role == role).order_by(User.created_at.desc(), User.id.desc())
        )
        query_result = await self.session.scalars(statement)

        return list(query_result)

    async def get_for_update(self, *, user_id: int) -> User | None:
        """Получить пользователя для изменения."""

        statement = select(User).where(User.id == user_id).with_for_update()
        query_result = await self.session.scalars(statement)

        return query_result.one_or_none()

    async def add(self, *, user: User) -> None:
        """Добавить пользователя."""

        self.session.add(user)
        await self.session.flush()

    async def list_by_ids(self, *, user_ids: set[int]) -> dict[int, User]:
        """Получить выбранные аккаунты."""

        if not user_ids:
            return {}

        statement = select(User).where(User.id.in_(user_ids))
        query_result = await self.session.scalars(statement)

        return {user.id: user for user in query_result}

    async def delete(self, *, user: User) -> None:
        """Удалить аккаунт."""

        await self.session.delete(user)
        await self.session.flush()
