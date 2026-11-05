"""Ответ платёжного провайдера."""

from decimal import Decimal

from pydantic import BaseModel, Field

from src.payments.enums import PaymentStatus


class GatewayAmount(BaseModel):
    """Сумма и валюта провайдера."""

    value: Decimal = Field(
        gt=0,
        max_digits=10,
        decimal_places=2,
    )
    currency: str


class GatewayConfirmation(BaseModel):
    """Переход на страницу оплаты."""

    confirmation_url: str | None = None


class GatewayPayment(BaseModel):
    """Проверенные поля ответа ЮKassa."""

    id: str
    status: PaymentStatus
    paid: bool
    amount: GatewayAmount
    confirmation: GatewayConfirmation | None = None

    @property
    def confirmation_url(self) -> str | None:
        """Ссылка на оплату, если она есть."""

        if self.confirmation is None:
            return None

        return self.confirmation.confirmation_url
