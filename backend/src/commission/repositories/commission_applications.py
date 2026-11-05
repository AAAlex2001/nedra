"""Хранение заявок кандидатов."""

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.commission.models.commission_application import CommissionApplication


class CommissionApplicationRepository:
    """Заявки в конкурсную комиссию."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def add(self, *, application: CommissionApplication) -> None:
        """Сохранить заявку."""

        self.session.add(application)
        await self.session.flush()

    async def list_all(self) -> list[CommissionApplication]:
        """Получить заявки от новых к старым."""

        statement = select(CommissionApplication).order_by(
            CommissionApplication.created_at.desc(),
            CommissionApplication.id.desc(),
        )
        query_result = await self.session.scalars(statement)

        return list(query_result)

    async def delete(self, *, application_id: int) -> bool:
        """Удалить заявку по номеру."""

        statement = (
            delete(CommissionApplication)
            .where(CommissionApplication.id == application_id)
            .returning(CommissionApplication.id)
        )
        deleted_application_id = await self.session.scalar(statement)

        return deleted_application_id is not None
