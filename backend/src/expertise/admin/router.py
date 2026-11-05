"""Управление работами администратором."""

from fastapi import APIRouter, Depends

from src.auth.admin.access import require_admin
from src.expertise.admin.dependencies import (
    get_delete_expertise_usecase,
    get_list_expertises_usecase,
    get_update_expertise_usecase,
)
from src.expertise.admin.schemas.expertise import ExpertiseAdminResponse, UpdateExpertiseRequest
from src.expertise.admin.usecases.delete_expertise import DeleteExpertiseUseCase
from src.expertise.admin.usecases.list_expertises import ListAdminExpertisesUseCase
from src.expertise.admin.usecases.update_expertise import UpdateExpertiseUseCase

router = APIRouter(
    prefix="/admin/expertises",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


@router.get("")
async def list_expertises(
    *, usecase: ListAdminExpertisesUseCase = Depends(get_list_expertises_usecase)
) -> list[ExpertiseAdminResponse]:
    """Получить все работы."""

    return await usecase.execute()


@router.patch("/{expertise_id}", status_code=204)
async def update_expertise(
    *,
    expertise_id: int,
    payload: UpdateExpertiseRequest,
    usecase: UpdateExpertiseUseCase = Depends(get_update_expertise_usecase),
) -> None:
    """Изменить работу."""

    await usecase.execute(
        expertise_id=expertise_id,
        payload=payload,
    )


@router.delete("/{expertise_id}", status_code=204)
async def delete_expertise(
    *,
    expertise_id: int,
    usecase: DeleteExpertiseUseCase = Depends(get_delete_expertise_usecase),
) -> None:
    """Удалить работу."""

    await usecase.execute(expertise_id=expertise_id)
