"""Зависимости управления экспертами."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repositories.expert_applications import ExpertApplicationRepository
from src.core.database import get_session
from src.users.admin.usecases.add_expert_certificate import AddExpertCertificateUseCase
from src.users.admin.usecases.delete_expert import DeleteExpertUseCase
from src.users.admin.usecases.delete_expert_certificate import DeleteExpertCertificateUseCase
from src.users.admin.usecases.list_customers import ListCustomersUseCase
from src.users.admin.usecases.list_experts import ListExpertsUseCase
from src.users.admin.usecases.update_expert import UpdateExpertUseCase
from src.users.admin.usecases.update_expert_certificate import UpdateExpertCertificateUseCase
from src.users.repositories.customer_activity import CustomerActivityRepository
from src.users.repositories.expert_certificates import ExpertCertificateRepository
from src.users.repositories.expert_profiles import ExpertProfileRepository
from src.users.repositories.users import UserRepository


def get_list_customers_usecase(
    *,
    session: AsyncSession = Depends(get_session),
) -> ListCustomersUseCase:
    """Просмотр заказчиков."""

    return ListCustomersUseCase(
        users=UserRepository(session=session),
        activity=CustomerActivityRepository(session=session),
    )


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
