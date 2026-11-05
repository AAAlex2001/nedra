"""Чтение и изменение аудита."""

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.models.audit import Audit
from src.audit.models.audit_team_member import AuditTeamMember


class AuditRepository:
    """Условия и этапы аудита."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def get_by_id(self, *, audit_id: int) -> Audit | None:
        """Найти аудит по номеру."""

        return await self.session.get(Audit, audit_id)

    async def get_for_update(self, *, audit_id: int) -> Audit | None:
        """Получить аудит для изменения."""

        statement = select(Audit).where(Audit.id == audit_id).with_for_update()
        return await self.session.scalar(statement)

    async def save(self, *, audit: Audit) -> None:
        """Сохранить изменения аудита."""

        self.session.add(audit)
        await self.session.flush()

    async def list_for_customer(self, *, user_id: int) -> list[Audit]:
        """Получить работы заказчика."""

        statement = (
            select(Audit)
            .where(Audit.customer_id == user_id)
            .order_by(Audit.created_at.desc(), Audit.id.desc())
        )
        query_result = await self.session.scalars(statement)
        return list(query_result)

    async def list_assigned(self, *, user_id: int) -> list[Audit]:
        """Получить назначенные работы."""

        team_audits = select(AuditTeamMember.audit_id).where(AuditTeamMember.user_id == user_id)
        statement = select(Audit).where(or_(Audit.lead_id == user_id, Audit.id.in_(team_audits)))
        query_result = await self.session.scalars(
            statement.order_by(Audit.created_at.desc(), Audit.id.desc())
        )
        return list(query_result)

    async def list_incoming(self) -> list[Audit]:
        """Получить аудиты без руководителя."""

        statement = select(Audit).where(Audit.status == "new", Audit.lead_id.is_(None))

        query_result = await self.session.scalars(
            statement.order_by(Audit.created_at.desc(), Audit.id.desc())
        )
        return list(query_result)

    async def list_all(self) -> list[Audit]:
        """Получить работы от новых к старым."""

        statement = select(Audit).order_by(Audit.created_at.desc(), Audit.id.desc())
        records = await self.session.scalars(statement)

        return list(records)

    async def delete(self, *, audit: Audit) -> None:
        """Удалить работу и зависимые записи."""

        await self.session.delete(audit)
        await self.session.flush()
