"""Заявки: репозиторий и фабрика сценария создания."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.services.requests.repo import RequestRepository
from app.services.requests.usecases.create_request import CreateRequestUseCase


def get_request_repository(
    session: AsyncSession = Depends(get_session),
) -> RequestRepository:
    """Репозиторий заявок с сессией текущего запроса."""

    return RequestRepository(session)


def get_create_request_usecase(
    requests: RequestRepository = Depends(get_request_repository),
) -> CreateRequestUseCase:
    """Сценарий создания заявки."""

    return CreateRequestUseCase(requests)
