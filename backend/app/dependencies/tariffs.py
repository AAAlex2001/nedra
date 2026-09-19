"""Тарифы: репозиторий и фабрика сценария сохранения."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.services.tariffs.repo import TariffRepository
from app.services.tariffs.usecases.save_tariffs import SaveTariffsUseCase


def get_tariff_repository(
    session: AsyncSession = Depends(get_session),
) -> TariffRepository:
    """Репозиторий тарифов с сессией текущего запроса."""

    return TariffRepository(session)


def get_save_tariffs_usecase(
    tariffs: TariffRepository = Depends(get_tariff_repository),
) -> SaveTariffsUseCase:
    """Сценарий сохранения сетки тарифов."""

    return SaveTariffsUseCase(tariffs)
