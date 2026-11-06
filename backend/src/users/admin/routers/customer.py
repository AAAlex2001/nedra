"""Управление заказчиками."""

from fastapi import APIRouter, Depends, Response

from src.auth.admin.access import require_admin
from src.users.admin.dependencies.customers import (
    get_delete_customer_usecase,
    get_list_customers_usecase,
)
from src.users.admin.schemas.customer import CustomerResponse
from src.users.admin.usecases.delete_customer import DeleteCustomerUseCase
from src.users.admin.usecases.list_customers import ListCustomersUseCase

router = APIRouter(
    prefix="/admin/customers",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


@router.get("")
async def list_customers(
    *,
    usecase: ListCustomersUseCase = Depends(get_list_customers_usecase),
) -> list[CustomerResponse]:
    """Получить заказчиков."""

    return await usecase.execute()


@router.delete("/{user_id}", status_code=204)
async def delete_customer(
    *,
    user_id: int,
    usecase: DeleteCustomerUseCase = Depends(get_delete_customer_usecase),
) -> Response:
    """Удалить заказчика."""

    await usecase.execute(user_id=user_id)

    return Response(status_code=204)
