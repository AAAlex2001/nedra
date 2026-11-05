"""Замечания и ответы заказчика."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.models.audit_remark import AuditRemark


class AuditRemarkRepository:
    """Хранение замечаний."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def add(self, *, remark: AuditRemark) -> None:
        """Добавить замечание."""

        self.session.add(remark)
        await self.session.flush()

    async def list_open(self, *, audit_id: int) -> list[AuditRemark]:
        """Получить неустранённые замечания."""

        statement = (
            select(AuditRemark)
            .where(
                AuditRemark.audit_id == audit_id,
                AuditRemark.resolved_at.is_(None),
            )
            .order_by(AuditRemark.id)
        )
        query_result = await self.session.scalars(statement)

        return list(query_result)

    async def list_for_audit(self, *, audit_id: int) -> list[AuditRemark]:
        """Получить все замечания аудита."""

        statement = (
            select(AuditRemark).where(AuditRemark.audit_id == audit_id).order_by(AuditRemark.id)
        )
        remarks = await self.session.scalars(statement)

        return list(remarks)
