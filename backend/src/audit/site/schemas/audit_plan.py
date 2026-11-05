"""План проведения аудита."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


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


class AuditPlanResponse(SubmitAuditPlanRequest):
    """Сохранённая версия плана."""

    version: int = 1

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


class RequestAuditPlanChangesRequest(BaseModel):
    """Замечания заказчика к плану."""

    model_config = ConfigDict(str_strip_whitespace=True)

    comment: str = Field(
        min_length=3,
        max_length=4000,
    )


class AuditTeamMemberResponse(BaseModel):
    """Участник аудиторской группы."""

    user_id: int
    full_name: str
    areas: list[str]
    lead: bool


class AuditPlanReviewResponse(BaseModel):
    """График и согласование плана."""

    schedule: AuditPlanResponse | None  # Последняя версия графика.
    comment: str | None  # Замечания заказчика к плану.
    sent_at: datetime | None  # Отправка на согласование.
    approved_at: datetime | None  # Согласование заказчиком.
