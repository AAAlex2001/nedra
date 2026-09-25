from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.billing import InvoiceStage


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
    reported_at: datetime | None
    paid_at: datetime | None


class ActOutSchema(BaseModel):
    """Акт выполненных работ. Отдельной таблицы нет: акт собирается из принятой экспертизы."""

    expertise_id: int
    number: str
    amount: Decimal | None
    subject: str
    signed_at: datetime
