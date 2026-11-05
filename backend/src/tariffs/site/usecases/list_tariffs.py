"""Просмотр действующих тарифов."""

from src.tariffs.repositories.tariffs import TariffRepository
from src.tariffs.schemas.tariff import TariffResponse


class ListTariffsUseCase:
    """Список тарифов для сайта."""

    def __init__(self, *, tariffs: TariffRepository) -> None:
        """Репозиторий тарифов."""

        self.tariffs = tariffs

    async def execute(self) -> list[TariffResponse]:
        """Получить действующие тарифы."""

        tariffs = await self.tariffs.list_all()

        return [TariffResponse.from_model(tariff=tariff) for tariff in tariffs]
