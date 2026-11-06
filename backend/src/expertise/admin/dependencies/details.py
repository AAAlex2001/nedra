"""Просмотр заявок администратором."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.contracts.repositories.contracts import ContractRepository
from src.core.database import get_session
from src.expertise.admin.usecases.get_expertise import GetAdminExpertiseUseCase
from src.expertise.admin.usecases.get_expertise_contract import (
    GetAdminExpertiseContractUseCase,
)
from src.expertise.admin.usecases.get_expertise_participants import (
    GetAdminExpertiseParticipantsUseCase,
)
from src.expertise.repositories.expertise_customers import ExpertiseCustomerRepository
from src.expertise.repositories.expertises import ExpertiseRepository
from src.users.repositories.users import UserRepository


def get_expertise_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> GetAdminExpertiseUseCase:
    """Просмотр данных заявки."""

    return GetAdminExpertiseUseCase(
        expertises=ExpertiseRepository(session=session),
    )


def get_expertise_participants_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> GetAdminExpertiseParticipantsUseCase:
    """Просмотр данных заявки."""

    return GetAdminExpertiseParticipantsUseCase(
        expertises=ExpertiseRepository(session=session),
        customers=ExpertiseCustomerRepository(session=session),
        users=UserRepository(session=session),
    )


def get_expertise_contract_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> GetAdminExpertiseContractUseCase:
    """Просмотр данных заявки."""

    return GetAdminExpertiseContractUseCase(
        expertises=ExpertiseRepository(session=session),
        contracts=ContractRepository(session=session),
    )
