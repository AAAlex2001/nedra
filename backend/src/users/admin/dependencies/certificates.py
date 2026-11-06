"""Удостоверения экспертов."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.users.admin.usecases.add_expert_certificate import AddExpertCertificateUseCase
from src.users.admin.usecases.delete_expert_certificate import (
    DeleteExpertCertificateUseCase,
)
from src.users.admin.usecases.update_expert_certificate import (
    UpdateExpertCertificateUseCase,
)
from src.users.repositories.expert_certificates import ExpertCertificateRepository
from src.users.repositories.expert_profiles import ExpertProfileRepository


def get_add_expert_certificate_usecase(
    *,
    session: AsyncSession = Depends(get_session),
) -> AddExpertCertificateUseCase:
    """Добавление удостоверения."""

    return AddExpertCertificateUseCase(
        session=session,
        profiles=ExpertProfileRepository(session=session),
        certificates=ExpertCertificateRepository(session=session),
    )


def get_update_expert_certificate_usecase(
    *,
    session: AsyncSession = Depends(get_session),
) -> UpdateExpertCertificateUseCase:
    """Изменение удостоверения."""

    return UpdateExpertCertificateUseCase(
        session=session,
        profiles=ExpertProfileRepository(session=session),
        certificates=ExpertCertificateRepository(session=session),
    )


def get_delete_expert_certificate_usecase(
    *,
    session: AsyncSession = Depends(get_session),
) -> DeleteExpertCertificateUseCase:
    """Удаление удостоверения."""

    return DeleteExpertCertificateUseCase(
        session=session,
        profiles=ExpertProfileRepository(session=session),
        certificates=ExpertCertificateRepository(session=session),
    )
