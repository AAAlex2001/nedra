"""Общие зависимости раздела."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.audit_letters import AuditLetters
from src.audit.repositories.audit_teams import AuditTeamRepository
from src.audit.repositories.audits import AuditRepository
from src.audit.site.audit_access import AuditAccess
from src.audit.site.audit_team_members import AuditTeamMembers
from src.core.email_sender import EmailSender
from src.core.settings import Settings
from src.users.repositories.expert_certificates import ExpertCertificateRepository
from src.users.repositories.expert_profiles import ExpertProfileRepository
from src.users.repositories.users import UserRepository


def get_audit_letters(*, settings: Settings) -> AuditLetters:
    """Письма участникам аудита."""

    return AuditLetters(
        sender=EmailSender(settings=settings),
        cabinet_url=settings.cabinet_url,
        manager_emails=settings.notify_emails,
    )


def get_audit_access(*, session: AsyncSession) -> AuditAccess:
    """Права просмотра аудита."""

    return AuditAccess(
        audits=AuditRepository(session=session),
        teams=AuditTeamRepository(session=session),
        profiles=ExpertProfileRepository(session=session),
    )


def get_audit_team_members(*, session: AsyncSession) -> AuditTeamMembers:
    """Имена и аттестация группы."""

    return AuditTeamMembers(
        teams=AuditTeamRepository(session=session),
        users=UserRepository(session=session),
        certificates=ExpertCertificateRepository(session=session),
    )
