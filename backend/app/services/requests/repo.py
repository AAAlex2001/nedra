"""Репозиторий заявок: только запросы к таблице requests."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.request import Request


class RequestRepository:
    """Доступ к таблице requests. Сессию получает снаружи, коммитит сам."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_all(self) -> list[Request]:
        """Все заявки, новые первыми."""

        stmt = select(Request).order_by(Request.created_at.desc())
        result = await self.db.execute(stmt)

        return list(result.scalars().all())

    async def get_by_id(self, request_id: int) -> Request | None:
        """Заявка по идентификатору или None."""

        return await self.db.get(Request, request_id)

    async def add(self, request: Request) -> Request:
        """Сохранить новую заявку."""

        self.db.add(request)
        await self.db.commit()
        await self.db.refresh(request)

        return request

    async def delete(self, request: Request) -> None:
        """Удалить заявку."""

        await self.db.delete(request)
        await self.db.commit()
