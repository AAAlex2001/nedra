"""Зависимости управления обращениями."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.requests.admin.usecases.delete_contact_request import (
    DeleteContactRequestUseCase,
)
from src.requests.admin.usecases.list_contact_requests import ListContactRequestsUseCase
from src.requests.repositories.contact_requests import ContactRequestRepository


def get_list_contact_requests_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> ListContactRequestsUseCase:
    """Просмотр обращений."""

    return ListContactRequestsUseCase(requests=ContactRequestRepository(session=session))


def get_delete_contact_request_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> DeleteContactRequestUseCase:
    """Удаление обращения."""

    return DeleteContactRequestUseCase(
        session=session,
        requests=ContactRequestRepository(session=session),
    )
