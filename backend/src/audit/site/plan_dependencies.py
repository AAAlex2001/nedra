"""Согласование плана."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.repositories.audit_applications import AuditApplicationRepository
from src.audit.repositories.audit_customers import AuditCustomerRepository
from src.audit.repositories.audit_plans import AuditPlanRepository
from src.audit.repositories.audit_teams import AuditTeamRepository
from src.audit.repositories.audits import AuditRepository
from src.audit.site.audit_plan_files import AuditPlanFiles
from src.audit.site.audit_plan_preparation import AuditPlanPreparation
from src.audit.site.dependencies import get_audit_access, get_audit_letters, get_audit_team_members
from src.audit.site.usecases.approve_audit_plan import ApproveAuditPlanUseCase
from src.audit.site.usecases.get_audit_plan import GetAuditPlanUseCase
from src.audit.site.usecases.request_audit_plan_changes import RequestAuditPlanChangesUseCase
from src.audit.site.usecases.submit_audit_plan import SubmitAuditPlanUseCase
from src.core.database import get_session
from src.core.file_storage import FileStorage
from src.core.settings import Settings, get_settings
from src.notifications.repositories.notifications import NotificationRepository
from src.users.repositories.users import UserRepository


def get_submit_audit_plan_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> SubmitAuditPlanUseCase:
    """Отправка плана на согласование."""

    return SubmitAuditPlanUseCase(
        preparation=AuditPlanPreparation(
            applications=AuditApplicationRepository(session=session),
            customers=AuditCustomerRepository(session=session),
            members=get_audit_team_members(session=session),
        ),
        session=session,
        audits=AuditRepository(session=session),
        plans=AuditPlanRepository(session=session),
        users=UserRepository(session=session),
        notifications=NotificationRepository(session=session),
        files=AuditPlanFiles(storage=FileStorage(directory=settings.private_dir)),
        letters=get_audit_letters(settings=settings),
    )


def get_approve_audit_plan_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> ApproveAuditPlanUseCase:
    """Согласование плана заказчиком."""

    return ApproveAuditPlanUseCase(
        applications=AuditApplicationRepository(session=session),
        session=session,
        audits=AuditRepository(session=session),
        plans=AuditPlanRepository(session=session),
        teams=AuditTeamRepository(session=session),
        users=UserRepository(session=session),
        notifications=NotificationRepository(session=session),
        letters=get_audit_letters(settings=settings),
    )


def get_request_audit_plan_changes_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> RequestAuditPlanChangesUseCase:
    """Возврат плана на доработку."""

    return RequestAuditPlanChangesUseCase(
        session=session,
        audits=AuditRepository(session=session),
        plans=AuditPlanRepository(session=session),
        users=UserRepository(session=session),
        notifications=NotificationRepository(session=session),
        letters=get_audit_letters(settings=settings),
    )


def get_audit_plan_usecase(*, session: AsyncSession = Depends(get_session)) -> GetAuditPlanUseCase:
    """План и согласование."""

    return GetAuditPlanUseCase(
        access=get_audit_access(session=session),
        plans=AuditPlanRepository(session=session),
    )
