"""Ответ заказчика на стоимость."""

from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from src.audit.enums import AuditOfferAnswer, AuditStatus
from src.audit.models.audit import Audit
from src.audit.options import MIN_AUDIT_PRICE
from src.audit.schemas.audit_conditions import AuditConditionsResponse
from src.audit.schemas.audit_dates import AuditDatesResponse


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


class AnswerAuditOfferResponse(BaseModel):
    """Условия и состояние аудита."""

    id: int  # Номер аудита.
    customer_id: int  # Номер заказчика.
    lead_id: int | None  # Номер руководителя группы.
    status: AuditStatus  # Текущий этап.
    result: str | None  # Результат заключения.
    conditions: AuditConditionsResponse  # Цена и пожелания заказчика.
    dates: AuditDatesResponse  # Даты прохождения этапов.

    @classmethod
    def from_model(cls, *, audit: Audit) -> "AnswerAuditOfferResponse":
        """Подготовить сведения об аудите."""

        return cls(
            id=audit.id,
            customer_id=audit.customer_id,
            lead_id=audit.lead_id,
            status=audit.status,
            result=audit.result,
            conditions=AuditConditionsResponse.from_model(audit=audit),
            dates=AuditDatesResponse.from_model(audit=audit),
        )
