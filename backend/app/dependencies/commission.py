"""Конкурсная комиссия: репозиторий и фабрика сценария подачи заявки."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.services.commission.repo import CommissionRepository
from app.services.commission.usecases.create_application import (
    CreateCommissionApplicationUseCase,
)


def get_commission_repository(
    session: AsyncSession = Depends(get_session),
) -> CommissionRepository:
    """Репозиторий заявок кандидатов с сессией текущего запроса."""

    return CommissionRepository(session)


def get_create_commission_application_usecase(
    applications: CommissionRepository = Depends(get_commission_repository),
) -> CreateCommissionApplicationUseCase:
    """Сценарий подачи заявки кандидата."""

    return CreateCommissionApplicationUseCase(applications)
