"""Изменение удостоверения в кабинете."""

from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator

from src.users.models.expert_certificate import ExpertCertificate
from src.users.models.expert_profile import ExpertProfile
from src.users.schemas.expert_certificate import ExpertCertificateResponse


class SaveExpertCertificateRequest(BaseModel):
    """Сведения об удостоверении."""

    area_code: str = Field(
        min_length=1,
        max_length=8,
    )
    object_code: str = Field(
        min_length=1,
        max_length=8,
    )
    category: int = Field(
        ge=1,
        le=3,
    )
    valid_until: date
    number: str = Field(
        min_length=1,
        max_length=64,
    )

    @field_validator(
        "number",
        mode="before",
    )
    @classmethod
    def strip_number(cls, certificate_number: object) -> object:
        """Убрать пробелы вокруг номера."""

        return (
            certificate_number.strip()
            if isinstance(certificate_number, str)
            else certificate_number
        )


class SaveExpertCertificateResponse(BaseModel):
    """Направления работы и удостоверения."""

    directions: list[str]
    approved_at: datetime
    certificates: list[ExpertCertificateResponse]

    @classmethod
    def from_model(
        cls,
        *,
        profile: ExpertProfile,
        certificates: list[ExpertCertificate],
    ) -> "SaveExpertCertificateResponse":
        """Подготовить профиль для кабинета."""

        return cls(
            directions=profile.directions,
            approved_at=profile.approved_at,
            certificates=[
                ExpertCertificateResponse.from_model(certificate=certificate)
                for certificate in certificates
            ],
        )
