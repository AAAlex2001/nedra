"""Зависимости изменения тарифов."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.tariffs.admin.usecases.save_tariffs import SaveTariffsUseCase
from src.tariffs.repositories.tariffs import TariffRepository


def get_save_tariffs_usecase(*, session: AsyncSession = Depends(get_session)) -> SaveTariffsUseCase:
    """Сохранение тарифов."""

    return SaveTariffsUseCase(
        session=session,
        tariffs=TariffRepository(session=session),
    )
