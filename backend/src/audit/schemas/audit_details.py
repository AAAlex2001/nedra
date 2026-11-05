"""Анкета аудита."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, model_validator


class AuditApplicantSchema(BaseModel):
    """Представитель заказчика."""

    full_name: str = Field(
        min_length=3,
        max_length=255,
    )
    position: str = Field(
        min_length=2,
        max_length=255,
    )
    organization: str = Field(
        min_length=2,
        max_length=500,
    )
    inn: str = Field(pattern=r"^\d{10}(\d{2})?$")
    phone: str = Field(
        min_length=10,
        max_length=32,
    )
    email: EmailStr
    by_proxy: bool = False


class AuditObjectSchema(BaseModel):
    """Опасный производственный объект."""

    reg_number: str = Field(
        min_length=1,
        max_length=64,
    )
    name: str = Field(
        min_length=2,
        max_length=500,
    )
    hazard_class: Literal["I", "II", "III", "IV"]
    address: str = Field(
        min_length=5,
        max_length=500,
    )
    industry: str = Field(
        min_length=2,
        max_length=500,
    )
    hazard_signs: list[Literal["substances", "pressure", "lifting", "melts", "mining", "grain"]] = (
        Field(
            min_length=1,
        )
    )


class AuditFleetSchema(BaseModel):
    """Все ОПО организации."""

    count: int = Field(
        ge=1,
        le=10000,
    )
    profile: str = Field(
        min_length=2,
        max_length=500,
    )
    multi_region: bool


AuditElement = Literal[
    "identification",
    "documentation",
    "production_control",
    "documents_compliance",
    "risk_measures",
    "incidents",
    "emergency",
    "insurance",
    "personnel",
    "contractors",
    "work_conditions",
    "equipment",
    "declaration",
    "justification",
    "intrusion",
    "instruments",
    "resources",
    "other",
]


class AuditParametersSchema(BaseModel):
    """Вид аудита и направления проверки."""

    kind: Literal["basic", "interim", "selective", "consultation"]
    use_sto: bool | None = None
    sto_name: str | None = Field(
        default=None,
        max_length=1000,
    )
    elements: list[AuditElement] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_parameters(self) -> "AuditParametersSchema":
        """Проверить параметры выбранного аудита."""

        if self.kind in ("basic", "interim") and self.use_sto is None:
            raise ValueError("Укажите, учитывать ли внутренние стандарты организации")

        if self.use_sto and not (self.sto_name or "").strip():
            raise ValueError("Укажите наименование и реквизиты СТО")

        if self.kind == "selective" and not self.elements:
            raise ValueError("Выберите хотя бы одно направление для аудита")

        return self


class AuditTimingSchema(BaseModel):
    """Период проведения аудита."""

    kind: Literal["custom", "month", "this_quarter", "next_quarter", "studying"]
    start: date | None = None
    end: date | None = None

    @model_validator(mode="after")
    def validate_period(self) -> "AuditTimingSchema":
        """Проверить выбранный период."""

        if self.kind != "custom":
            return self

        if self.start is None or self.end is None:
            raise ValueError("Укажите период проведения аудита")

        if self.start > self.end:
            raise ValueError("Начало периода позже его окончания")

        return self


class AuditBudgetSchema(BaseModel):
    """Бюджет и возможность обсуждать цену."""

    mode: Literal["custom", "none"]
    negotiation: Literal["yes", "no", "on_scope"]


class AuditDetailsSchema(BaseModel):
    """Объекты и условия аудита."""

    applicant: AuditApplicantSchema
    scope: Literal["one", "all", "selected"]
    objects: list[AuditObjectSchema] = Field(
        default_factory=list,
        max_length=200,
    )
    fleet: AuditFleetSchema | None = None
    stages: list[Literal["planning", "documents", "onsite", "report"]] = Field(min_length=1)
    params: AuditParametersSchema
    timing: AuditTimingSchema
    budget: AuditBudgetSchema

    @model_validator(mode="after")
    def validate_objects(self) -> "AuditDetailsSchema":
        """Проверить состав объектов."""

        if self.scope == "one" and len(self.objects) != 1:
            raise ValueError("Укажите сведения об одном ОПО")

        if self.scope == "selected" and not self.objects:
            raise ValueError("Добавьте хотя бы один ОПО")

        if self.scope == "all" and self.fleet is None:
            raise ValueError("Укажите сведения обо всех ОПО организации")

        return self
