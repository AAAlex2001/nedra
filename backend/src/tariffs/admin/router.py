"""Управление тарифами."""

from fastapi import APIRouter, Depends

from src.auth.admin.access import require_admin
from src.tariffs.admin.dependencies import get_save_tariffs_usecase
from src.tariffs.admin.schemas.save_tariffs import SaveTariffsRequest
from src.tariffs.admin.usecases.save_tariffs import SaveTariffsUseCase
from src.tariffs.schemas.tariff import TariffResponse

router = APIRouter(
    prefix="/admin/tariffs",
    tags=["tariffs"],
    dependencies=[Depends(require_admin)],
)


@router.put("")
async def save_tariffs(
    payload: SaveTariffsRequest,
    usecase: SaveTariffsUseCase = Depends(get_save_tariffs_usecase),
) -> list[TariffResponse]:
    """Изменить тарифы."""

    return await usecase.execute(payload=payload)
