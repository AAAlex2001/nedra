"""Сессии базы данных."""

from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Основа моделей базы данных."""


async def get_session(*, request: Request) -> AsyncIterator[AsyncSession]:
    """Открыть сессию на время запроса."""

    async with request.app.state.session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
