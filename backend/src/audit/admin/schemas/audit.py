"""Управление заявками аудита."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from src.audit.enums import AuditStatus


class AuditAdminResponse(BaseModel):
    """Строка списка работ."""

    id: int  # Номер работы.
    status: AuditStatus  # Текущий этап.
    customer_id: int  # Заказчик.
    customer_name: str  # Имя заказчика.
    lead_id: int | None  # Исполнитель.
    lead_name: str | None  # Имя исполнителя.
    object_name: str | None  # Наименование объекта.
    price: Decimal | None  # Стоимость работы.
    created_at: datetime  # Дата подачи.


class UpdateAuditRequest(BaseModel):
    """Изменения администратора."""

    status: AuditStatus  # Новый этап работы.
    price: Decimal | None = Field(
        ge=0,
        max_digits=10,
        decimal_places=2,
    )  # Стоимость в рублях.
    lead_id: int | None = Field(ge=1)  # Назначенный исполнитель.
