from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.payment import PaymentStatus


class PaymentCreateSchema(BaseModel):
    """Данные для создания платежа."""

    amount: Decimal = Field(
        ...,
        gt=0,
        max_digits=10,
        decimal_places=2,
        description="Сумма в рублях, например 15000.00",
    )
    description: str = Field(..., min_length=3, max_length=128, description="Назначение платежа")


class PaymentOutSchema(BaseModel):
    """Платёж для клиента. Ссылку на оплату отдаём, пока платёж не завершён."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID платежа")
    amount: Decimal = Field(..., description="Сумма")
    currency: str = Field(..., description="Валюта")
    description: str = Field(..., description="Назначение")
    status: PaymentStatus = Field(..., description="Статус")
    confirmation_url: str | None = Field(None, description="Куда отправить пользователя для оплаты")
    created_at: datetime = Field(..., description="Когда создан")
    paid_at: datetime | None = Field(None, description="Когда оплачен")


class WebhookObjectSchema(BaseModel):
    """Часть уведомления ЮKassa с самим платежом. Нам нужен только id."""

    model_config = ConfigDict(extra="ignore")

    id: str = Field(..., description="ID платежа в ЮKassa")


class WebhookSchema(BaseModel):
    """Уведомление ЮKassa. Статус из тела не берём — перепроверяем через API."""

    model_config = ConfigDict(extra="ignore")

    type: str = Field(..., description="Всегда notification")
    event: str = Field(..., description="Например payment.succeeded")
    object: WebhookObjectSchema
