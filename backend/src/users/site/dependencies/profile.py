"""Изменение профиля."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repositories.expert_applications import ExpertApplicationRepository
from src.core.database import get_session
from src.users.repositories.users import UserRepository
from src.users.site.usecases.update_profile import UpdateProfileUseCase


def get_update_profile_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> UpdateProfileUseCase:
    """Изменение профиля."""

    return UpdateProfileUseCase(
        session=session,
        users=UserRepository(session=session),
        applications=ExpertApplicationRepository(session=session),
    )
