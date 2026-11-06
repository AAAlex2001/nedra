"""Управление тарифами."""

from fastapi import APIRouter, Depends

from src.auth.admin.access import require_admin
from src.tariffs.admin.dependencies.tariffs import get_save_tariffs_usecase
from src.tariffs.admin.schemas.save_tariffs import (
    SaveTariffsRequest,
    SaveTariffsResponse,
)
from src.tariffs.admin.usecases.save_tariffs import SaveTariffsUseCase

router = APIRouter(
    prefix="/admin/tariffs",
    tags=["tariffs"],
    dependencies=[Depends(require_admin)],
)


@router.put("")
async def save_tariffs(
    payload: SaveTariffsRequest,
    usecase: SaveTariffsUseCase = Depends(get_save_tariffs_usecase),
) -> list[SaveTariffsResponse]:
    """Изменить тарифы."""

    return await usecase.execute(payload=payload)
