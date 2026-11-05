"""Регистрация эксперта."""

from pydantic import BaseModel, Field

from src.auth.enums import ApplicationStatus
from src.auth.site.schemas.register import RegisterRequest
from src.users.schemas.expert_certificate import ExpertCertificateRequest


class CreateExpertApplicationRequest(RegisterRequest):
    """Контакты и аттестация нового эксперта."""

    directions: list[str] = Field(min_length=1)
    certificates: list[ExpertCertificateRequest] = Field(min_length=1)


class ExpertApplicationCreatedResponse(BaseModel):
    """Номер и статус поданной заявки."""

    id: int
    status: ApplicationStatus
