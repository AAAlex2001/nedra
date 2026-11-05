"""Анкеты заказчиков аудита."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.models.audit_application import AuditApplication


class AuditApplicationRepository:
    """Чтение анкеты аудита."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def get(self, *, audit_id: int) -> AuditApplication | None:
        """Получить анкету."""

        return await self.session.get(AuditApplication, audit_id)

    async def list_by_audit_ids(self, *, audit_ids: set[int]) -> dict[int, AuditApplication]:
        """Получить анкеты выбранных аудитов."""

        if not audit_ids:
            return {}

        statement = select(AuditApplication).where(AuditApplication.audit_id.in_(audit_ids))
        applications = await self.session.scalars(statement)

        return {application.audit_id: application for application in applications}
