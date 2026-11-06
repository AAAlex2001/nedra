"""Зависимости профиля эксперта."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repositories.expert_applications import ExpertApplicationRepository
from src.core.database import get_session
from src.users.repositories.expert_certificates import ExpertCertificateRepository
from src.users.repositories.expert_profiles import ExpertProfileRepository
from src.users.site.usecases.get_expert_profile import GetExpertProfileUseCase
from src.users.site.usecases.update_expert_directions import (
    UpdateExpertDirectionsUseCase,
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
