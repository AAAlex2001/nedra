from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.admin import require_admin
from app.dependencies.tariffs import get_save_tariffs_usecase, get_tariff_repository
from app.schemas.tariff import TariffSchema, TariffsSaveSchema
from app.services.tariffs.exceptions import InvalidTariffError
from app.services.tariffs.repo import TariffRepository
from app.services.tariffs.usecases.save_tariffs import SaveTariffsUseCase


router = APIRouter(tags=["tariffs"])


@router.get("/tariffs")
async def get_tariffs(
    tariffs: TariffRepository = Depends(get_tariff_repository),
) -> list[TariffSchema]:
    """Публичный список тарифов для страницы цен."""

    items = await tariffs.list_all()

    return [TariffSchema.model_validate(item) for item in items]


@router.put("/admin/tariffs", dependencies=[Depends(require_admin)])
async def save_tariffs(
    payload: TariffsSaveSchema,
    usecase: SaveTariffsUseCase = Depends(get_save_tariffs_usecase),
) -> list[TariffSchema]:
    """Сохранить изменённые ячейки сетки. Возвращает актуальный список целиком."""

    try:
        items = await usecase.execute(payload.items)
    except InvalidTariffError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

    return [TariffSchema.model_validate(item) for item in items]
