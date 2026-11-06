"""Зависимости просмотра тарифов."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.tariffs.repositories.tariffs import TariffRepository
from src.tariffs.site.usecases.list_tariffs import ListTariffsUseCase


def get_list_tariffs_usecase(*, session: AsyncSession = Depends(get_session)) -> ListTariffsUseCase:
    """Просмотр тарифов."""

    return ListTariffsUseCase(tariffs=TariffRepository(session=session))
