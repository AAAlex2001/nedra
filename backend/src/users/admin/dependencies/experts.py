"""Управление экспертами."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repositories.expert_applications import ExpertApplicationRepository
from src.core.database import get_session
from src.users.admin.usecases.delete_expert import DeleteExpertUseCase
from src.users.admin.usecases.list_experts import ListExpertsUseCase
from src.users.admin.usecases.update_expert import UpdateExpertUseCase
from src.users.repositories.expert_certificates import ExpertCertificateRepository
from src.users.repositories.expert_profiles import ExpertProfileRepository
from src.users.repositories.users import UserRepository


def get_list_experts_usecase(*, session: AsyncSession = Depends(get_session)) -> ListExpertsUseCase:
    """Просмотр экспертов."""

    return ListExpertsUseCase(
        users=UserRepository(session=session),
        profiles=ExpertProfileRepository(session=session),
        certificates=ExpertCertificateRepository(session=session),
    )


def get_update_expert_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> UpdateExpertUseCase:
    """Изменение профиля эксперта."""

    return UpdateExpertUseCase(
        session=session,
        users=UserRepository(session=session),
        profiles=ExpertProfileRepository(session=session),
        certificates=ExpertCertificateRepository(session=session),
        applications=ExpertApplicationRepository(session=session),
    )


def get_delete_expert_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> DeleteExpertUseCase:
    """Удаление аккаунта эксперта."""

    return DeleteExpertUseCase(
        session=session,
        users=UserRepository(session=session),
        profiles=ExpertProfileRepository(session=session),
        applications=ExpertApplicationRepository(session=session),
    )
