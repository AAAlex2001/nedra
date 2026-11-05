"""Зависимости управления заявками кандидатов."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.commission.admin.usecases.delete_commission_application import (
    DeleteCommissionApplicationUseCase,
)
from src.commission.admin.usecases.list_commission_applications import (
    ListCommissionApplicationsUseCase,
)
from src.commission.repositories.commission_applications import CommissionApplicationRepository
from src.core.database import get_session


def get_list_commission_applications_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> ListCommissionApplicationsUseCase:
    """Просмотр заявок кандидатов."""

    return ListCommissionApplicationsUseCase(
        applications=CommissionApplicationRepository(session=session)
    )


def get_delete_commission_application_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> DeleteCommissionApplicationUseCase:
    """Удаление заявки кандидата."""

    return DeleteCommissionApplicationUseCase(
        session=session,
        applications=CommissionApplicationRepository(session=session),
    )
