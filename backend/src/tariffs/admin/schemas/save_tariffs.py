"""Изменение тарифов."""

from decimal import Decimal

from pydantic import BaseModel, Field


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
