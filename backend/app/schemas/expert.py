from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.expert import ApplicationStatus
from app.schemas.user import PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH


class DirectionSchema(BaseModel):
    """Направление работы эксперта."""

    code: str
    title: str


class ExpertiseObjectSchema(BaseModel):
    """Объект экспертизы: код, короткая подпись и расшифровка."""

    code: str
    label: str
    title: str


class AttestationAreaSchema(BaseModel):
    """Область аттестации и коды объектов, по которым она выдаётся."""

    code: str
    title: str
    objects: list[str]


class ExpertCatalogSchema(BaseModel):
    """Весь справочник для формы заявки: направления, области, объекты, категории."""

    directions: list[DirectionSchema]
    areas: list[AttestationAreaSchema]
    objects: list[ExpertiseObjectSchema]
    categories: list[int]


class CertificateInSchema(BaseModel):
    """Удостоверение в заявке. scan_index — номер файла в списке загруженных сканов."""

    area_code: str = Field(..., max_length=8, description="Область аттестации, например Э1")
    object_code: str = Field(..., max_length=8, description="Объект экспертизы, например kl_tp")
    category: int = Field(..., ge=1, le=3, description="Категория эксперта")
    valid_until: date = Field(..., description="Срок действия удостоверения")
    scan_index: int | None = Field(None, ge=0, description="Индекс файла скана среди загруженных")


class ExpertApplicationInSchema(BaseModel):
    """Заявка эксперта на регистрацию."""

    email: EmailStr
    password: str = Field(..., min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: str = Field(..., min_length=10, max_length=32)
    directions: list[str] = Field(..., min_length=1, description="Коды направлений работы")
    certificates: list[CertificateInSchema] = Field(..., min_length=1)


class CertificateOutSchema(BaseModel):
    """Удостоверение наружу. Путь к файлу не отдаём, только факт наличия скана."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    area_code: str
    object_code: str
    category: int
    valid_until: date
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


class ExpertProfileOutSchema(BaseModel):
    """Профиль эксперта для личного кабинета."""

    directions: list[str]
    approved_at: datetime
    certificates: list[CertificateOutSchema]
