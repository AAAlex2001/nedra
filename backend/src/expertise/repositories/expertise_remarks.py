"""Замечания и ответы заказчика."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.expertise.models.expertise_remark import ExpertiseRemark


class ExpertiseRemarkRepository:
    """Хранение замечаний."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def add(self, *, remark: ExpertiseRemark) -> None:
        """Добавить замечание."""

        self.session.add(remark)
        await self.session.flush()

    async def list_open(self, *, expertise_id: int) -> list[ExpertiseRemark]:
        """Получить неустранённые замечания."""

        statement = (
            select(ExpertiseRemark)
            .where(
                ExpertiseRemark.expertise_id == expertise_id,
                ExpertiseRemark.resolved_at.is_(None),
            )
            .order_by(ExpertiseRemark.id)
        )
        query_result = await self.session.scalars(statement)

        return list(query_result)

    async def list_for_expertise(self, *, expertise_id: int) -> list[ExpertiseRemark]:
        """Получить все замечания экспертизы."""

        statement = (
            select(ExpertiseRemark)
            .where(ExpertiseRemark.expertise_id == expertise_id)
            .order_by(ExpertiseRemark.id)
        )
        remarks = await self.session.scalars(statement)

        return list(remarks)
