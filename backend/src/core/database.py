"""Подключение к базе данных и выдача асинхронных сессий."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from src.core.config import get_settings


class Base(DeclarativeBase):
    """Базовый класс ORM-моделей."""

    pass


def create_engine() -> AsyncEngine:
    """Создаёт асинхронный движок SQLAlchemy."""

    settings = get_settings()
    return create_async_engine(
        settings.database_url,
        pool_pre_ping=True,
        echo=settings.debug,
    )


engine: AsyncEngine = create_engine()
SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Выдаёт сессию БД и откатывает изменения при ошибке."""

    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
