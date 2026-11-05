"""Акт в списке документов заказчика."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class ActResponse(BaseModel):
    """Номер, сумма и работа по акту."""

    audit_id: int | None  # Номер аудита.
    expertise_id: int | None  # Номер экспертизы.
    number: str  # Номер акта с обозначением услуги.
    amount: Decimal | None  # Согласованная стоимость.
    subject: str  # Наименование работы.
    signed_at: datetime  # Дата приёмки.
