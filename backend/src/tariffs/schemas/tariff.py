"""Стоимость услуги."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from src.tariffs.models.tariff import Tariff


class TariffResponse(BaseModel):
    """Действующий тариф."""

    area_code: str
    object_code: str
    price: Decimal
    updated_at: datetime

    @classmethod
    def from_model(cls, *, tariff: Tariff) -> "TariffResponse":
        """Подготовить данные тарифа."""

        return cls(
            area_code=tariff.area_code,
            object_code=tariff.object_code,
            price=tariff.price,
            updated_at=tariff.updated_at,
        )
