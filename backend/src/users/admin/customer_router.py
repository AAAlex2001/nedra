"""Просмотр заказчиков администратором."""

from fastapi import APIRouter, Depends

from src.auth.admin.access import require_admin
from src.users.admin.dependencies import get_list_customers_usecase
from src.users.admin.schemas.customer import CustomerResponse
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
