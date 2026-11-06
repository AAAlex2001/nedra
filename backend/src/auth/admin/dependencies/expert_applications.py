"""Зависимости рассмотрения заявок экспертов."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.admin.expert_application_letters import ExpertApplicationReviewLetters
from src.auth.admin.usecases.approve_expert_application import (
    ApproveExpertApplicationUseCase,
)
from src.auth.admin.usecases.get_application_certificate_scan import (
    GetApplicationCertificateScanUseCase,
)
from src.auth.admin.usecases.get_expert_application import GetExpertApplicationUseCase
from src.auth.admin.usecases.list_expert_applications import (
    ListExpertApplicationsUseCase,
)
from src.auth.admin.usecases.reject_expert_application import (
    RejectExpertApplicationUseCase,
)
from src.auth.repositories.expert_applications import ExpertApplicationRepository
from src.core.database import get_session
from src.core.email_sender import EmailSender
from src.core.file_storage import FileStorage
from src.core.settings import Settings, get_settings
from src.users.repositories.expert_certificates import ExpertCertificateRepository
from src.users.repositories.expert_profiles import ExpertProfileRepository
from src.users.repositories.users import UserRepository


def get_application_certificate_scan_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> GetApplicationCertificateScanUseCase:
    """Просмотр скана из заявки."""

    return GetApplicationCertificateScanUseCase(
        applications=ExpertApplicationRepository(session=session),
        certificates=ExpertCertificateRepository(session=session),
        storage=FileStorage(directory=settings.private_dir),
    )


def get_expert_application_review_letters(*, settings: Settings) -> ExpertApplicationReviewLetters:
    """Письма о решении по заявке."""

    return ExpertApplicationReviewLetters(
        sender=EmailSender(settings=settings),
        site_url=settings.site_url,
    )


def get_approve_expert_application_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> ApproveExpertApplicationUseCase:
    """Одобрение регистрации эксперта."""

    return ApproveExpertApplicationUseCase(
        session=session,
        applications=ExpertApplicationRepository(session=session),
        users=UserRepository(session=session),
        profiles=ExpertProfileRepository(session=session),
        certificates=ExpertCertificateRepository(session=session),
        letters=get_expert_application_review_letters(settings=settings),
    )


def get_reject_expert_application_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> RejectExpertApplicationUseCase:
    """Отклонение регистрации эксперта."""

    return RejectExpertApplicationUseCase(
        session=session,
        applications=ExpertApplicationRepository(session=session),
        certificates=ExpertCertificateRepository(session=session),
        letters=get_expert_application_review_letters(settings=settings),
    )


def get_list_expert_applications_usecase(
    *,
    session: AsyncSession = Depends(get_session),
) -> ListExpertApplicationsUseCase:
    """Список заявок экспертов."""

    return ListExpertApplicationsUseCase(
        applications=ExpertApplicationRepository(session=session),
        certificates=ExpertCertificateRepository(session=session),
        profiles=ExpertProfileRepository(session=session),
    )


def get_expert_application_usecase(
    *,
    session: AsyncSession = Depends(get_session),
) -> GetExpertApplicationUseCase:
    """Просмотр заявки эксперта."""

    return GetExpertApplicationUseCase(
        applications=ExpertApplicationRepository(session=session),
        certificates=ExpertCertificateRepository(session=session),
        profiles=ExpertProfileRepository(session=session),
    )
