"""Репозиторий пользователей: только запросы к таблице users, без бизнес-правил."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.services.users.exceptions import EmailAlreadyTakenError


class UserRepository:
    """Доступ к таблице users. Сессию получает снаружи, коммитит сам."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        """Пользователь по id или None."""

        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Пользователь по email или None. Email ожидается уже нормализованным."""

        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def list_by_role(self, role: UserRole) -> list[User]:
        """Все пользователи с ролью, новые сверху. Колонка role проиндексирована."""

        stmt = select(User).where(User.role == role).order_by(User.created_at.desc())
        result = await self.db.execute(stmt)

        return list(result.scalars().all())

    async def save(self, user: User) -> User:
        """Сохранить изменения существующего пользователя."""

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def delete(self, user: User) -> None:
        """Удалить пользователя. Профиль, удостоверения и уведомления база удалит каскадом."""

        await self.db.delete(user)
        await self.db.commit()

    async def add(self, user: User) -> User:
        """Сохранить нового пользователя.

        Уникальность email гарантирует индекс в БД. Если два запроса на один
        email пришли одновременно, второй получит IntegrityError — переводим
        его в понятную бизнес-ошибку.
        """

        self.db.add(user)

        try:
            await self.db.commit()
        except IntegrityError as error:
            await self.db.rollback()
            raise EmailAlreadyTakenError(f"Email {user.email} уже занят") from error

        await self.db.refresh(user)

        return user
