"""Сценарий сохранения сетки тарифов из админки."""

from app.models.tariff import Tariff
from app.schemas.tariff import TariffInSchema
from app.services.experts.catalog import AREA_BY_CODE, OBJECT_BY_CODE
from app.services.tariffs.exceptions import InvalidTariffError
from app.services.tariffs.repo import TariffRepository


class SaveTariffsUseCase:
    """Принять сетку из админки: каждая ячейка — пара «область × объект» и цена.

    Пустая цена значит «удалить тариф». Все ячейки сохраняются одной транзакцией:
    либо применяется вся сетка, либо ничего.
    """

    def __init__(self, tariffs: TariffRepository) -> None:
        self.tariffs = tariffs

    async def execute(self, cells: list[TariffInSchema]) -> list[Tariff]:
        """Сохранить сетку и вернуть актуальный список тарифов. Бросает InvalidTariffError."""

        for cell in cells:
            self.check_cell(cell)

        for cell in cells:
            await self.apply_cell(cell)

        await self.tariffs.commit()

        return await self.tariffs.list_all()

    def check_cell(self, cell: TariffInSchema) -> None:
        """Ячейка с ценой должна быть допустимой парой по справочнику. Удаление не проверяем."""

        if cell.price is None:
            return

        area = AREA_BY_CODE.get(cell.area_code)
        if area is None:
            raise InvalidTariffError(f"Неизвестная область аттестации: {cell.area_code}")

        if cell.object_code not in OBJECT_BY_CODE:
            raise InvalidTariffError(f"Неизвестный объект экспертизы: {cell.object_code}")

        if cell.object_code not in area.objects:
            label = OBJECT_BY_CODE[cell.object_code].label
            raise InvalidTariffError(f"По области {cell.area_code} нет объекта {label}")

    async def apply_cell(self, cell: TariffInSchema) -> None:
        """Найти тариф этой пары в базе и обновить, создать или удалить его."""

        tariff = await self.tariffs.get(cell.area_code, cell.object_code)

        if cell.price is None:
            if tariff is not None:
                await self.tariffs.remove(tariff)
            return

        self.tariffs.set_price(tariff, cell.area_code, cell.object_code, cell.price)
