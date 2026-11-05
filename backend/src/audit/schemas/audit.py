"""Основные сведения об аудите."""

from pydantic import BaseModel

from src.audit.enums import AuditStatus
from src.audit.models.audit import Audit
from src.audit.schemas.audit_conditions import AuditConditionsResponse
from src.audit.schemas.audit_dates import AuditDatesResponse


class AuditResponse(BaseModel):
    """Условия и состояние аудита."""

    id: int  # Номер аудита.
    customer_id: int  # Номер заказчика.
    lead_id: int | None  # Номер руководителя группы.
    status: AuditStatus  # Текущий этап.
    result: str | None  # Результат заключения.
    conditions: AuditConditionsResponse  # Цена и пожелания заказчика.
    dates: AuditDatesResponse  # Даты прохождения этапов.

    @classmethod
    def from_model(cls, *, audit: Audit) -> "AuditResponse":
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
