"""Тарифы на сайте."""

from fastapi import APIRouter, Depends

from src.tariffs.schemas.tariff import TariffResponse
from src.tariffs.site.dependencies import get_list_tariffs_usecase
from src.tariffs.site.usecases.list_tariffs import ListTariffsUseCase

router = APIRouter(
    prefix="/tariffs",
    tags=["tariffs"],
)


@router.get("")
async def list_tariffs(
    usecase: ListTariffsUseCase = Depends(get_list_tariffs_usecase),
) -> list[TariffResponse]:
    """Получить тарифы."""

    return await usecase.execute()
