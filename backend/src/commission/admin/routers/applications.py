"""Управление заявками кандидатов."""

from fastapi import APIRouter, Depends

from src.auth.admin.access import require_admin
from src.commission.admin.dependencies.applications import (
    get_delete_commission_application_usecase,
    get_list_commission_applications_usecase,
)
from src.commission.admin.usecases.delete_commission_application import (
    DeleteCommissionApplicationUseCase,
)
from src.commission.admin.usecases.list_commission_applications import (
    ListCommissionApplicationsUseCase,
)
from src.commission.schemas.commission_application import CommissionApplicationResponse

router = APIRouter(
    prefix="/admin/commission/applications",
    tags=["commission"],
    dependencies=[Depends(require_admin)],
)


@router.get("")
async def list_commission_applications(
    usecase: ListCommissionApplicationsUseCase = Depends(get_list_commission_applications_usecase),
) -> list[CommissionApplicationResponse]:
    """Получить заявки кандидатов."""

    return await usecase.execute()


@router.delete(
    "/{application_id}",
    status_code=204,
)
async def delete_commission_application(
    application_id: int,
    usecase: DeleteCommissionApplicationUseCase = Depends(
        get_delete_commission_application_usecase
    ),
) -> None:
    """Удалить заявку кандидата."""

    await usecase.execute(application_id=application_id)
