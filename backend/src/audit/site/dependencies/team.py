"""Группа аудиторов."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.repositories.audit_plans import AuditPlanRepository
from src.audit.repositories.audit_teams import AuditTeamRepository
from src.audit.repositories.audits import AuditRepository
from src.audit.site.audit_team_members import AuditTeamMembers
from src.audit.site.dependencies.access import get_audit_access
from src.audit.site.usecases.get_audit_team import GetAuditTeamUseCase
from src.audit.site.usecases.list_auditors import ListAuditorsUseCase
from src.audit.site.usecases.set_audit_team import SetAuditTeamUseCase
from src.core.database import get_session
from src.notifications.repositories.notifications import NotificationRepository
from src.users.repositories.expert_certificates import ExpertCertificateRepository
from src.users.repositories.expert_profiles import ExpertProfileRepository
from src.users.repositories.users import UserRepository


def get_list_auditors_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> ListAuditorsUseCase:
    """Выбор аудиторов для группы."""

    return ListAuditorsUseCase(
        profiles=ExpertProfileRepository(session=session),
        certificates=ExpertCertificateRepository(session=session),
    )


def get_set_audit_team_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> SetAuditTeamUseCase:
    """Изменение состава группы."""

    return SetAuditTeamUseCase(
        session=session,
        audits=AuditRepository(session=session),
        teams=AuditTeamRepository(session=session),
        profiles=ExpertProfileRepository(session=session),
        notifications=NotificationRepository(session=session),
    )


def get_audit_team_usecase(*, session: AsyncSession = Depends(get_session)) -> GetAuditTeamUseCase:
    """Группа аудиторов."""

    return GetAuditTeamUseCase(
        access=get_audit_access(session=session),
        plans=AuditPlanRepository(session=session),
        members=get_audit_team_members(session=session),
    )


def get_audit_team_members(*, session: AsyncSession) -> AuditTeamMembers:
    """Имена и аттестация группы."""

    return AuditTeamMembers(
        teams=AuditTeamRepository(session=session),
        users=UserRepository(session=session),
        certificates=ExpertCertificateRepository(session=session),
    )
