"""Удостоверения эксперта."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.core.file_storage import FileStorage
from src.core.settings import Settings, get_settings
from src.users.repositories.expert_certificates import ExpertCertificateRepository
from src.users.repositories.expert_profiles import ExpertProfileRepository
from src.users.site.dependencies.letters import get_expert_letters
from src.users.site.usecases.add_expert_certificate import AddExpertCertificateUseCase
from src.users.site.usecases.delete_expert_certificate import (
    DeleteExpertCertificateUseCase,
)
from src.users.site.usecases.get_expert_certificate_scan import (
    GetExpertCertificateScanUseCase,
)
from src.users.site.usecases.update_expert_certificate import (
    UpdateExpertCertificateUseCase,
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
