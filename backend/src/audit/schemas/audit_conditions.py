"""Условия оплаты аудита."""

from decimal import Decimal

from pydantic import BaseModel

from src.audit.models.audit import Audit


class AuditConditionsResponse(BaseModel):
    """Бюджет, предложения и согласованная цена."""

    customer_budget: Decimal | None  # Исходный бюджет заказчика.
    offer_price: Decimal | None  # Предложенная руководителем цена.
    counter_price: Decimal | None  # Встречная цена заказчика.
    agreed_price: Decimal | None  # Согласованная стоимость.
    negotiation_allowed: bool  # Готовность обсуждать стоимость.
    comment: str | None  # Комментарий заказчика.

    @classmethod
    def from_model(cls, *, audit: Audit) -> "AuditConditionsResponse":
        """Подготовить условия аудита."""

        return cls(
            customer_budget=audit.customer_budget,
            offer_price=audit.offer_price,
            counter_price=audit.counter_price,
            agreed_price=audit.agreed_price,
            negotiation_allowed=audit.negotiation_allowed,
            comment=audit.comment,
        )
