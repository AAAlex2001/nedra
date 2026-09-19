from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class TariffSchema(BaseModel):
    """Тариф наружу: пара кодов и цена в рублях."""

    model_config = ConfigDict(from_attributes=True)

    area_code: str = Field(..., description="Область аттестации, например Э1")
    object_code: str = Field(..., description="Объект экспертизы, например tu")
    price: Decimal = Field(..., description="Стоимость в рублях")
    updated_at: datetime


class TariffInSchema(BaseModel):
    """Одна ячейка сетки тарифов. price = null означает «удалить тариф»."""

    area_code: str = Field(..., max_length=8)
    object_code: str = Field(..., max_length=8)
    price: Decimal | None = Field(None, gt=0, max_digits=10, decimal_places=2)


class TariffsSaveSchema(BaseModel):
    """Пакет изменений из админской сетки."""

    items: list[TariffInSchema] = Field(..., min_length=1)
