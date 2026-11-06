"""Управление заказчиками."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.users.admin.usecases.delete_customer import DeleteCustomerUseCase
from src.users.admin.usecases.list_customers import ListCustomersUseCase
from src.users.repositories.customer_activity import CustomerActivityRepository
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


def get_delete_customer_usecase(
    *,
    session: AsyncSession = Depends(get_session),
) -> DeleteCustomerUseCase:
    """Удаление заказчика."""

    return DeleteCustomerUseCase(
        session=session,
        users=UserRepository(session=session),
    )
