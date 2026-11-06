"""Общие зависимости раздела."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.repositories.audit_teams import AuditTeamRepository
from src.audit.repositories.audits import AuditRepository
from src.audit.site.audit_access import AuditAccess
from src.users.repositories.expert_profiles import ExpertProfileRepository


def get_audit_access(*, session: AsyncSession) -> AuditAccess:
    """Права просмотра аудита."""

    return AuditAccess(
        audits=AuditRepository(session=session),
        teams=AuditTeamRepository(session=session),
        profiles=ExpertProfileRepository(session=session),
    )
