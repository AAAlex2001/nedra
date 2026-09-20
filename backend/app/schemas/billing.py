from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.billing import InvoiceStage


class CompanyInSchema(BaseModel):
    """Реквизиты организации заказчика из формы в кабинете."""

    name: str = Field(..., min_length=2, max_length=255, description="Название организации")
    inn: str = Field(..., min_length=10, max_length=12, description="ИНН")
    kpp: str | None = Field(None, max_length=9, description="КПП, у предпринимателя его нет")
    address: str = Field(..., min_length=5, max_length=500, description="Юридический адрес")


class CompanyOutSchema(BaseModel):
    """Реквизиты организации наружу."""

    model_config = ConfigDict(from_attributes=True)

    name: str
    inn: str
    kpp: str | None
    address: str
    updated_at: datetime


class InvoiceOutSchema(BaseModel):
    """Счёт для кабинета заказчика и админки."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    number: str
    expertise_id: int
    stage: InvoiceStage
    amount: Decimal
    payer_name: str
    payer_inn: str
    created_at: datetime
    paid_at: datetime | None


class ActOutSchema(BaseModel):
    """Акт выполненных работ. Отдельной таблицы нет: акт собирается из принятой экспертизы."""

    expertise_id: int
    number: str
    amount: Decimal | None
    subject: str
    signed_at: datetime
