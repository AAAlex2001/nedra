"""Хранение планов аудита."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.models.audit_document import AuditDocument
from src.audit.models.audit_plan import AuditPlan


class AuditPlanRepository:
    """План аудита и его документ."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def get(self, *, audit_id: int) -> AuditPlan | None:
        """Найти план аудита."""

        return await self.session.get(AuditPlan, audit_id)

    async def save(self, *, plan: AuditPlan) -> None:
        """Сохранить изменения плана."""

        self.session.add(plan)
        await self.session.flush()

    async def save_with_document(
        self,
        *,
        plan: AuditPlan,
        document: AuditDocument,
    ) -> None:
        """Сохранить план с документом."""

        self.session.add_all([plan, document])
        await self.session.flush()
