"""Хранение аудиторских групп."""

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.models.audit_team_member import AuditTeamMember


class AuditTeamRepository:
    """Участники аудита."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def list_user_ids(self, *, audit_id: int) -> list[int]:
        """Получить номера участников группы."""

        statement = (
            select(AuditTeamMember.user_id)
            .where(AuditTeamMember.audit_id == audit_id)
            .order_by(AuditTeamMember.user_id)
        )
        query_result = await self.session.scalars(statement)

        return list(query_result)

    async def replace(
        self,
        *,
        audit_id: int,
        user_ids: list[int],
    ) -> None:
        """Заменить состав группы."""

        statement = delete(AuditTeamMember).where(AuditTeamMember.audit_id == audit_id)
        await self.session.execute(statement)

        for user_id in user_ids:
            self.session.add(
                AuditTeamMember(
                    audit_id=audit_id,
                    user_id=user_id,
                )
            )

        await self.session.flush()
