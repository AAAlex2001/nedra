"""Эксперт в административной части."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.users.models.expert_certificate import ExpertCertificate
from src.users.models.expert_profile import ExpertProfile
from src.users.models.user import User
from src.users.schemas.expert_certificate import ExpertCertificateResponse


class UpdateExpertRequest(BaseModel):
    """Изменение профиля эксперта."""

    full_name: str = Field(
        min_length=2,
        max_length=255,
    )
    phone: str = Field(
        min_length=10,
        max_length=32,
    )
    directions: list[str] = Field(min_length=1)
    audit_lead: bool = False

    @field_validator(
        "full_name",
        mode="before",
    )
    @classmethod
    def strip_name_spaces(cls, full_name: object) -> object:
        """Убрать пробелы вокруг имени."""

        return full_name.strip() if isinstance(full_name, str) else full_name


class ExpertResponse(BaseModel):
    """Аккаунт, направления и удостоверения эксперта."""

    user_id: int
    email: EmailStr
    full_name: str
    phone: str
    directions: list[str]
    audit_lead: bool
    approved_at: datetime
    certificates: list[ExpertCertificateResponse]

    @classmethod
    def from_model(
        cls,
        *,
        user: User,
        profile: ExpertProfile,
        certificates: list[ExpertCertificate],
    ) -> "ExpertResponse":
        """Подготовить профиль эксперта."""

        return cls(
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            directions=profile.directions,
            audit_lead=profile.audit_lead,
            approved_at=profile.approved_at,
            certificates=[
                ExpertCertificateResponse.from_model(certificate=certificate)
                for certificate in certificates
            ],
        )
