from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, model_validator

AuditScope = Literal["one", "all", "selected"]

AuditStage = Literal["planning", "documents", "onsite", "report"]

HazardClass = Literal["I", "II", "III", "IV"]

HazardSign = Literal["substances", "pressure", "lifting", "melts", "mining", "grain"]

AuditKind = Literal["basic", "interim", "selective", "consultation"]

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

TimingKind = Literal["custom", "month", "this_quarter", "next_quarter", "studying"]

BudgetMode = Literal["custom", "none"]

Negotiation = Literal["yes", "no", "on_scope"]


class AuditApplicantSchema(BaseModel):
    """Сведения о заявителе: контакты представителя для связи.

    by_proxy — заявитель не руководитель и действует по доверенности:
    тогда к заявке обязательно прикладывается доверенность.
    """

    full_name: str = Field(..., min_length=3, max_length=255, description="ФИО представителя")
    position: str = Field(..., min_length=2, max_length=255, description="Должность")
    organization: str = Field(
        ..., min_length=2, max_length=500, description="Наименование организации"
    )
    inn: str = Field(..., pattern=r"^\d{10}(\d{2})?$", description="ИНН организации")
    phone: str = Field(..., min_length=10, max_length=32, description="Контактный телефон")
    email: EmailStr = Field(..., description="Корпоративный e-mail")
    by_proxy: bool = Field(False, description="Заявитель действует по доверенности")


class AuditObjectSchema(BaseModel):
    """Опасный производственный объект, который проверяется."""

    reg_number: str = Field(
        ..., min_length=1, max_length=64, description="Регистрационный номер ОПО"
    )
    name: str = Field(..., min_length=2, max_length=500, description="Наименование ОПО")
    hazard_class: HazardClass = Field(..., description="Класс опасности ОПО")
    address: str = Field(
        ..., min_length=5, max_length=500, description="Адрес (местонахождение) ОПО"
    )
    industry: str = Field(
        ..., min_length=2, max_length=500,
        description="Отраслевая специфика / вид деятельности на ОПО",
    )
    hazard_signs: list[HazardSign] = Field(
        ..., min_length=1, description="Признаки опасности ОПО по Приложению 1 к 116-ФЗ"
    )


class AuditFleetSchema(BaseModel):
    """Сведения обо всех ОПО организации, когда аудит проводится по всем."""

    count: int = Field(..., ge=1, le=10000, description="Общее количество ОПО")
    profile: str = Field(
        ..., min_length=2, max_length=500, description="Основной отраслевой профиль"
    )
    multi_region: bool = Field(..., description="Есть ОПО в разных субъектах РФ")


class AuditParamsSchema(BaseModel):
    """Тип аудита и то, что от него зависит: СТО организации или элементы СУПБ."""

    kind: AuditKind = Field(..., description="Тип запрашиваемого аудита")
    use_sto: bool | None = Field(
        None, description="Учитывать СТО организации: для базового и промежуточного аудита"
    )
    sto_name: str | None = Field(None, max_length=1000, description="Наименование и реквизиты СТО")
    elements: list[AuditElement] = Field(
        default_factory=list, description="Элементы СУПБ для выборочного аудита"
    )

    @model_validator(mode="after")
    def match_kind(self) -> "AuditParamsSchema":
        """Под тип аудита — свои уточнения."""

        if self.kind in ("basic", "interim") and self.use_sto is None:
            raise ValueError("Укажите, учитывать ли внутренние стандарты организации")

        if self.use_sto and not (self.sto_name or "").strip():
            raise ValueError("Укажите наименование и реквизиты СТО")

        if self.kind == "selective" and not self.elements:
            raise ValueError("Выберите хотя бы одно направление для аудита")

        return self


class AuditTimingSchema(BaseModel):
    """Желаемые сроки проведения аудита. Свой срок — период с … по …."""

    kind: TimingKind
    start: date | None = None
    end: date | None = None

    @model_validator(mode="after")
    def require_period(self) -> "AuditTimingSchema":
        """Свой срок задаётся периодом, начало не позже конца."""

        if self.kind != "custom":
            return self

        if self.start is None or self.end is None:
            raise ValueError("Укажите период проведения аудита")

        if self.start > self.end:
            raise ValueError("Начало периода позже его окончания")

        return self


class AuditBudgetSchema(BaseModel):
    """Планируемый бюджет и готовность обсуждать стоимость."""

    mode: BudgetMode = Field(..., description="custom — своя сумма, none — бюджет не установлен")
    negotiation: Negotiation = Field(..., description="Возможность обсуждения стоимости")


class AuditDetailsSchema(BaseModel):
    """Заявитель, масштаб, ОПО, этапы, параметры, сроки и бюджет аудита.

    one — один ОПО в objects, selected — несколько ОПО в objects,
    all — сведения обо всех ОПО в fleet.
    """

    applicant: AuditApplicantSchema
    scope: AuditScope = Field(..., description="one, all или selected")
    objects: list[AuditObjectSchema] = Field(default_factory=list, max_length=200)
    fleet: AuditFleetSchema | None = None
    stages: list[AuditStage] = Field(..., min_length=1, description="Этапы аудита")
    params: AuditParamsSchema
    timing: AuditTimingSchema
    budget: AuditBudgetSchema

    @model_validator(mode="after")
    def match_scope(self) -> "AuditDetailsSchema":
        """Под каждый масштаб — свои сведения об объектах."""

        if self.scope == "one" and len(self.objects) != 1:
            raise ValueError("Укажите сведения об ОПО")

        if self.scope == "selected" and not self.objects:
            raise ValueError("Добавьте хотя бы один ОПО")

        if self.scope == "all" and self.fleet is None:
            raise ValueError("Укажите сведения об ОПО организации")

        return self


class AuditPlanInSchema(BaseModel):
    """Что руководитель группы заполняет в Плане аудита.

    Цели и критерии аудита стандартные и стоят в шаблоне Программы.
    Даты выездного этапа нужны, если заказчик выбрал выездной этап.
    Время совещаний — если совещания проводятся.
    """

    documents_start: date
    documents_end: date
    onsite_start: date | None = None
    onsite_end: date | None = None
    meetings: bool = Field(True, description="Проводить вступительное и заключительное совещания")
    opening_at: datetime | None = None
    closing_at: datetime | None = None
    meeting_link: str | None = Field(None, max_length=500, description="Ссылка на видеосвязь")
    workshops: str | None = Field(
        None, max_length=2000, description="Цеха и участки для выездного этапа"
    )
    interviewees: str = Field(
        ..., min_length=2, max_length=2000, description="Должностные лица для интервью"
    )

    @model_validator(mode="after")
    def check_schedule(self) -> "AuditPlanInSchema":
        """Периоды идут по порядку, у совещаний есть время."""

        if self.documents_start > self.documents_end:
            raise ValueError("Начало документарного этапа позже его окончания")

        if (self.onsite_start is None) != (self.onsite_end is None):
            raise ValueError("Укажите обе даты выездного этапа")

        if self.onsite_start and self.onsite_end and self.onsite_start > self.onsite_end:
            raise ValueError("Начало выездного этапа позже его окончания")

        if self.meetings and (self.opening_at is None or self.closing_at is None):
            raise ValueError("Укажите время вступительного и заключительного совещаний")

        return self


class AuditPlanSchema(AuditPlanInSchema):
    """Сохранённый План аудита: номер версии растёт с каждой отправкой заказчику."""

    version: int = 1


class AuditTeamMemberSchema(BaseModel):
    """Аудитор группы: ФИО, области аттестации и руководитель ли он."""

    user_id: int
    full_name: str
    areas: list[str]
    lead: bool
