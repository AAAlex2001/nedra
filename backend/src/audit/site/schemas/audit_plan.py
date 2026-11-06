"""Сохранённый план аудита."""

from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator

from src.audit.site.schemas.submit_audit_plan import (
    SubmitAuditPlanRequest,
)


class AuditPlanResponse(BaseModel):
    """Сохранённая версия плана."""

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
    version: int = 1

    @model_validator(mode="after")
    def validate_schedule(self) -> "AuditPlanResponse":
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

    @classmethod
    def from_request(
        cls,
        *,
        payload: SubmitAuditPlanRequest,
        version: int,
    ) -> "AuditPlanResponse":
        """Подготовить новую версию плана."""

        return cls(
            documents_start=payload.documents_start,
            documents_end=payload.documents_end,
            onsite_start=payload.onsite_start,
            onsite_end=payload.onsite_end,
            meetings=payload.meetings,
            opening_at=payload.opening_at,
            closing_at=payload.closing_at,
            meeting_link=payload.meeting_link,
            workshops=payload.workshops,
            interviewees=payload.interviewees,
            version=version,
        )


class AuditPlanReviewResponse(BaseModel):
    """График и согласование плана."""

    schedule: AuditPlanResponse | None  # Последняя версия графика.
    comment: str | None  # Замечания заказчика к плану.
    sent_at: datetime | None  # Отправка на согласование.
    approved_at: datetime | None  # Согласование заказчиком.
