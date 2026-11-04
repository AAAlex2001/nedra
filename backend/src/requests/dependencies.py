"""Зависимости FastAPI для заявок."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.requests.repositories.requests import RequestRepository
from src.requests.use_cases import (
    CreateRequestUseCase,
    DeleteRequestUseCase,
    ListRequestsUseCase,
)


def get_request_repository(
    *,
    session: AsyncSession = Depends(get_db),
) -> RequestRepository:
    """Возвращает репозиторий заявок."""

    return RequestRepository(session=session)


def get_create_request_use_case(
    *,
    repository: RequestRepository = Depends(get_request_repository),
) -> CreateRequestUseCase:
    """Возвращает use case создания заявки."""

    return CreateRequestUseCase(requests=repository)


def get_list_requests_use_case(
    *,
    repository: RequestRepository = Depends(get_request_repository),
) -> ListRequestsUseCase:
    """Возвращает use case получения списка заявок."""

    return ListRequestsUseCase(requests=repository)


def get_delete_request_use_case(
    *,
    repository: RequestRepository = Depends(get_request_repository),
) -> DeleteRequestUseCase:
    """Возвращает use case удаления заявки."""

    return DeleteRequestUseCase(requests=repository)
