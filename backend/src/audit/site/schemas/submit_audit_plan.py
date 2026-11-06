"""Отправка плана аудита."""

from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator

from src.audit.enums import AuditStatus
from src.audit.models.audit import Audit
from src.audit.schemas.audit_conditions import AuditConditionsResponse
from src.audit.schemas.audit_dates import AuditDatesResponse


class SubmitAuditPlanRequest(BaseModel):
    """Сроки проверки и совещания."""

    documents_start: date
    documents_end: date
    onsite_start: date | None = None
    onsite_end: date | None = None
    meetings: bool = True
    opening_at: datetime | None = None
    closing_at: datetime | None = None
    meeting_link: str | None = Field(
        default=None,
        max_length=500,
    )
    workshops: str | None = Field(
        default=None,
        max_length=2000,
    )
    interviewees: str = Field(
        min_length=2,
        max_length=2000,
    )

    @model_validator(mode="after")
    def validate_schedule(self) -> "SubmitAuditPlanRequest":
        """Проверить даты проверки и совещаний."""

        if self.documents_start > self.documents_end:
            raise ValueError("Начало документарного этапа позже его окончания")

        if self.onsite_start is None and self.onsite_end is not None:
            raise ValueError("Укажите обе даты выездного этапа")

        if self.onsite_end is None and self.onsite_start is not None:
            raise ValueError("Укажите обе даты выездного этапа")

        if self.onsite_start is not None and self.onsite_end is not None:
            if self.onsite_start > self.onsite_end:
                raise ValueError("Начало выездного этапа позже его окончания")

        if self.meetings and (self.opening_at is None or self.closing_at is None):
            raise ValueError("Укажите время вступительного и заключительного совещаний")

        return self


class SubmitAuditPlanResponse(BaseModel):
    """Условия и состояние аудита."""

    id: int  # Номер аудита.
    customer_id: int  # Номер заказчика.
    lead_id: int | None  # Номер руководителя группы.
    status: AuditStatus  # Текущий этап.
    result: str | None  # Результат заключения.
    conditions: AuditConditionsResponse  # Цена и пожелания заказчика.
    dates: AuditDatesResponse  # Даты прохождения этапов.

    @classmethod
    def from_model(cls, *, audit: Audit) -> "SubmitAuditPlanResponse":
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
