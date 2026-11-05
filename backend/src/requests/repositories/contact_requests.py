"""Хранение обращений."""

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.requests.models.contact_request import ContactRequest


class ContactRequestRepository:
    """Обращения с сайта."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def add(self, *, contact_request: ContactRequest) -> None:
        """Сохранить обращение."""

        self.session.add(contact_request)
        await self.session.flush()

    async def list_all(self) -> list[ContactRequest]:
        """Получить обращения от новых к старым."""

        statement = select(ContactRequest).order_by(
            ContactRequest.created_at.desc(),
            ContactRequest.id.desc(),
        )
        query_result = await self.session.scalars(statement)

        return list(query_result)

    async def delete(self, *, request_id: int) -> bool:
        """Удалить обращение по номеру."""

        statement = (
            delete(ContactRequest)
            .where(ContactRequest.id == request_id)
            .returning(ContactRequest.id)
        )
        deleted_request_id = await self.session.scalar(statement)

        return deleted_request_id is not None
