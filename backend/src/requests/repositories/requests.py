"""Репозиторий заявок."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.requests.models import Request


class RequestRepository:
    """Доступ к данным заявок с сайта."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Принимает сессию БД."""

        self.session = session

    async def list_all(self) -> list[Request]:
        """Возвращает все заявки, новые первыми."""

        result = await self.session.execute(
            select(Request).order_by(Request.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, *, request_id: int) -> Request | None:
        """Возвращает заявку по идентификатору."""

        return await self.session.get(Request, request_id)

    async def add(self, *, request: Request) -> Request:
        """Добавляет заявку и коммитит изменения."""

        self.session.add(request)
        await self.session.commit()
        await self.session.refresh(request)
        return request

    async def delete(self, *, request: Request) -> None:
        """Удаляет заявку и коммитит изменения."""

        await self.session.delete(request)
        await self.session.commit()
