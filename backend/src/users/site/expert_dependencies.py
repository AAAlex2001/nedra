"""Зависимости профиля эксперта."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repositories.expert_applications import ExpertApplicationRepository
from src.core.database import get_session
from src.core.email_sender import EmailSender
from src.core.file_storage import FileStorage
from src.core.settings import Settings, get_settings
from src.users.repositories.expert_certificates import ExpertCertificateRepository
from src.users.repositories.expert_profiles import ExpertProfileRepository
from src.users.site.expert_letters import ExpertLetters
from src.users.site.usecases.add_expert_certificate import AddExpertCertificateUseCase
from src.users.site.usecases.delete_expert_certificate import DeleteExpertCertificateUseCase
from src.users.site.usecases.get_expert_certificate_scan import GetExpertCertificateScanUseCase
from src.users.site.usecases.get_expert_profile import GetExpertProfileUseCase
from src.users.site.usecases.update_expert_certificate import UpdateExpertCertificateUseCase
from src.users.site.usecases.update_expert_directions import UpdateExpertDirectionsUseCase


def get_expert_letters(*, settings: Settings) -> ExpertLetters:
    """Письма менеджерам об удостоверениях."""

    return ExpertLetters(
        sender=EmailSender(settings=settings),
        manager_emails=settings.notify_emails,
    )


def get_expert_profile_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> GetExpertProfileUseCase:
    """Просмотр профиля эксперта."""

    return GetExpertProfileUseCase(
        profiles=ExpertProfileRepository(session=session),
        certificates=ExpertCertificateRepository(session=session),
    )


def get_update_expert_directions_usecase(
    *,
    session: AsyncSession = Depends(get_session),
) -> UpdateExpertDirectionsUseCase:
    """Изменение направлений работы."""

    return UpdateExpertDirectionsUseCase(
        session=session,
        profiles=ExpertProfileRepository(session=session),
        certificates=ExpertCertificateRepository(session=session),
        applications=ExpertApplicationRepository(session=session),
    )


def get_add_expert_certificate_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> AddExpertCertificateUseCase:
    """Добавление удостоверения эксперта."""

    return AddExpertCertificateUseCase(
        session=session,
        profiles=ExpertProfileRepository(session=session),
        certificates=ExpertCertificateRepository(session=session),
        letters=get_expert_letters(settings=settings),
    )


def get_update_expert_certificate_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> UpdateExpertCertificateUseCase:
    """Изменение удостоверения эксперта."""

    return UpdateExpertCertificateUseCase(
        session=session,
        profiles=ExpertProfileRepository(session=session),
        certificates=ExpertCertificateRepository(session=session),
        letters=get_expert_letters(settings=settings),
    )


def get_delete_expert_certificate_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> DeleteExpertCertificateUseCase:
    """Удаление удостоверения эксперта."""

    return DeleteExpertCertificateUseCase(
        session=session,
        profiles=ExpertProfileRepository(session=session),
        certificates=ExpertCertificateRepository(session=session),
        letters=get_expert_letters(settings=settings),
    )


def get_expert_certificate_scan_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> GetExpertCertificateScanUseCase:
    """Просмотр скана удостоверения."""

    return GetExpertCertificateScanUseCase(
        certificates=ExpertCertificateRepository(session=session),
        storage=FileStorage(directory=settings.private_dir),
    )
