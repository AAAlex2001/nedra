"""Ответ заказчика на стоимость."""

from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from src.audit.enums import AuditOfferAnswer
from src.audit.options import MIN_AUDIT_PRICE


class AnswerAuditOfferRequest(BaseModel):
    """Ответ на предложение аудитора."""

    answer: AuditOfferAnswer
    price: Decimal | None = Field(
        default=None,
        ge=MIN_AUDIT_PRICE,
        max_digits=10,
        decimal_places=2,
    )

    @model_validator(mode="after")
    def validate_counter_price(self) -> "AnswerAuditOfferRequest":
        """Проверить наличие встречной цены."""

        if self.answer == AuditOfferAnswer.COUNTER and self.price is None:
            raise ValueError("Укажите свою цену")

        return self
