from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.expert import ApplicationStatus
from app.schemas.user import PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH


class DirectionSchema(BaseModel):
    """Направление работы эксперта."""

    code: str
    title: str


class ExpertiseObjectSchema(BaseModel):
    """Объект экспертизы: код, короткая подпись, расшифровка и пояснение для заказчика."""

    code: str
    label: str
    title: str
    description: str


class AttestationAreaSchema(BaseModel):
    """Область аттестации и коды объектов, по которым она выдаётся."""

    code: str
    title: str
    objects: list[str]


class HazardClassSchema(BaseModel):
    """Класс опасности ОПО и минимальная категория эксперта, которая по нему допускается."""

    hazard_class: int
    category: int


class ExpertCatalogSchema(BaseModel):
    """Весь справочник для форм: направления, области, объекты, категории, классы опасности."""

    directions: list[DirectionSchema]
    areas: list[AttestationAreaSchema]
    objects: list[ExpertiseObjectSchema]
    categories: list[int]
    hazard_classes: list[HazardClassSchema]


class CertificateInSchema(BaseModel):
    """Удостоверение в заявке."""

    area_code: str = Field(..., max_length=8, description="Область аттестации, например Э1")
    object_code: str = Field(..., max_length=8, description="Объект экспертизы, например kl_tp")
    category: int = Field(..., ge=1, le=3, description="Категория эксперта")
    valid_until: date = Field(
        ..., description="Дата окончания срока действия квалификационного удостоверения"
    )
    number: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="Номер квалификационного удостоверения или номер регистрации в ЕРУЛ",
    )


class ExpertApplicationInSchema(BaseModel):
    """Заявка эксперта.

    Контакты и пароль обязательны для нового человека. Если заявку подаёт
    вошедший заказчик, они берутся из его аккаунта и здесь не нужны.
    """

    email: EmailStr | None = None
    password: str | None = Field(
        None, min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH
    )
    full_name: str | None = Field(None, min_length=2, max_length=255)
    phone: str | None = Field(None, min_length=10, max_length=32)
    directions: list[str] = Field(..., min_length=1, description="Коды направлений работы")
    certificates: list[CertificateInSchema] = Field(..., min_length=1)


class CertificateOutSchema(BaseModel):
    """Удостоверение наружу. Скан есть только у старых заявок, путь к нему не отдаём."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    area_code: str
    object_code: str
    category: int
    valid_until: date
    number: str | None
    scan_name: str | None


class ExpertApplicationOutSchema(BaseModel):
    """Заявка для админки."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    phone: str
    directions: list[str]
    status: ApplicationStatus
    admin_comment: str | None
    user_id: int | None
    created_at: datetime
    reviewed_at: datetime | None
    certificates: list[CertificateOutSchema]


class ExpertApplicationCreatedSchema(BaseModel):
    """Ответ на подачу заявки."""

    id: int
    status: ApplicationStatus


class RejectApplicationSchema(BaseModel):
    """Причина отклонения, её увидит эксперт в письме."""

    comment: str = Field(..., min_length=3, max_length=1000)


class ExpertUpdateSchema(BaseModel):
    """Что админ правит у эксперта. Email не меняем: по нему человек входит."""

    full_name: str = Field(..., min_length=2, max_length=255)
    phone: str = Field(..., min_length=10, max_length=32)
    directions: list[str] = Field(..., min_length=1, description="Коды направлений работы")


class ExpertOutSchema(BaseModel):
    """Эксперт в админке: аккаунт, направления и удостоверения."""

    user_id: int
    email: EmailStr
    full_name: str
    phone: str
    directions: list[str]
    approved_at: datetime
    certificates: list[CertificateOutSchema]


class ExpertProfileOutSchema(BaseModel):
    """Профиль эксперта для личного кабинета."""

    directions: list[str]
    approved_at: datetime
    certificates: list[CertificateOutSchema]
