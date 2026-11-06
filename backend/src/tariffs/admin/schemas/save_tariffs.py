"""Изменение тарифов."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from src.tariffs.models.tariff import Tariff


class TariffChange(BaseModel):
    """Новая цена; пустая цена удаляет тариф."""

    area_code: str = Field(max_length=8)
    object_code: str = Field(max_length=8)
    price: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=10,
        decimal_places=2,
    )


class SaveTariffsRequest(BaseModel):
    """Изменения сетки тарифов."""

    items: list[TariffChange] = Field(min_length=1)


class SaveTariffsResponse(BaseModel):
    """Действующий тариф."""

    area_code: str
    object_code: str
    price: Decimal
    updated_at: datetime

    @classmethod
    def from_model(cls, *, tariff: Tariff) -> "SaveTariffsResponse":
        """Подготовить данные тарифа."""

        return cls(
            area_code=tariff.area_code,
            object_code=tariff.object_code,
            price=tariff.price,
            updated_at=tariff.updated_at,
        )
