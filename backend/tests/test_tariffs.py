"""Тесты сценария сохранения тарифов без БД."""

import asyncio
from decimal import Decimal

import pytest

from app.models.tariff import Tariff
from app.schemas.tariff import TariffInSchema
from app.services.tariffs.exceptions import InvalidTariffError
from app.services.tariffs.usecases.save_tariffs import SaveTariffsUseCase


class FakeTariffRepository:
    """Тарифы в словаре по паре кодов."""

    def __init__(self) -> None:
        self.items: dict[tuple[str, str], Tariff] = {}
        self.committed = False

    async def list_all(self) -> list[Tariff]:
        return list(self.items.values())

    async def get(self, area_code: str, object_code: str) -> Tariff | None:
        return self.items.get((area_code, object_code))

    def set_price(self, tariff: Tariff | None, area_code: str, object_code: str, price: Decimal) -> None:
        if tariff is None:
            self.items[(area_code, object_code)] = Tariff(
                area_code=area_code, object_code=object_code, price=price
            )
        else:
            tariff.price = price

    async def remove(self, tariff: Tariff) -> None:
        del self.items[(tariff.area_code, tariff.object_code)]

    async def commit(self) -> None:
        self.committed = True


def test_save_adds_updates_and_removes() -> None:
    repo = FakeTariffRepository()
    usecase = SaveTariffsUseCase(repo)

    asyncio.run(
        usecase.execute(
            [
                TariffInSchema(area_code="Э1", object_code="tu", price=Decimal("15000")),
                TariffInSchema(area_code="Э4", object_code="d", price=Decimal("20000")),
            ]
        )
    )
    assert repo.items[("Э1", "tu")].price == Decimal("15000")
    assert repo.committed

    result = asyncio.run(
        usecase.execute(
            [
                TariffInSchema(area_code="Э1", object_code="tu", price=Decimal("16000")),
                TariffInSchema(area_code="Э4", object_code="d", price=None),
            ]
        )
    )

    assert len(result) == 1
    assert repo.items[("Э1", "tu")].price == Decimal("16000")
    assert ("Э4", "d") not in repo.items


def test_save_rejects_unknown_pair() -> None:
    usecase = SaveTariffsUseCase(FakeTariffRepository())

    with pytest.raises(InvalidTariffError):
        asyncio.run(
            usecase.execute([TariffInSchema(area_code="Э1", object_code="d", price=Decimal("1"))])
        )

    with pytest.raises(InvalidTariffError):
        asyncio.run(
            usecase.execute([TariffInSchema(area_code="Э77", object_code="tu", price=Decimal("1"))])
        )


def test_removing_missing_tariff_is_noop() -> None:
    repo = FakeTariffRepository()
    usecase = SaveTariffsUseCase(repo)

    result = asyncio.run(
        usecase.execute([TariffInSchema(area_code="Э1", object_code="tu", price=None)])
    )

    assert result == []
