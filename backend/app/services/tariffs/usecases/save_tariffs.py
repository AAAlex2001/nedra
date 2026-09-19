"""Сценарий сохранения сетки тарифов из админки."""

from app.models.tariff import Tariff
from app.schemas.tariff import TariffInSchema
from app.services.experts.catalog import AREA_BY_CODE, OBJECT_BY_CODE
from app.services.tariffs.exceptions import InvalidTariffError
from app.services.tariffs.repo import TariffRepository


class SaveTariffsUseCase:
    """Проверить каждую ячейку по справочнику и применить изменения одной транзакцией."""

    def __init__(self, tariffs: TariffRepository) -> None:
        self.tariffs = tariffs

    async def execute(self, items: list[TariffInSchema]) -> list[Tariff]:
        """Обновить, добавить или удалить тарифы. Бросает InvalidTariffError."""

        for item in items:
            self.validate_pair(item.area_code, item.object_code)

        for item in items:
            existing = await self.tariffs.get(item.area_code, item.object_code)

            if item.price is None:
                if existing is not None:
                    await self.tariffs.remove(existing)
                continue

            self.tariffs.set_price(existing, item.area_code, item.object_code, item.price)

        await self.tariffs.commit()

        return await self.tariffs.list_all()

    @staticmethod
    def validate_pair(area_code: str, object_code: str) -> None:
        """Область и объект должны быть в справочнике, а объект — выдаваться по области."""

        area = AREA_BY_CODE.get(area_code)
        if area is None:
            raise InvalidTariffError(f"Неизвестная область аттестации: {area_code}")

        if object_code not in OBJECT_BY_CODE:
            raise InvalidTariffError(f"Неизвестный объект экспертизы: {object_code}")

        if object_code not in area.objects:
            label = OBJECT_BY_CODE[object_code].label
            raise InvalidTariffError(f"По области {area_code} нет объекта {label}")
