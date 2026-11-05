"""Удостоверения эксперта."""

from datetime import date

from pydantic import BaseModel, Field, field_validator

from src.users.models.expert_certificate import ExpertCertificate


class ExpertCertificateRequest(BaseModel):
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


class ExpertCertificateResponse(BaseModel):
    """Сохранённое удостоверение."""

    id: int
    area_code: str
    object_code: str
    category: int
    valid_until: date
    number: str | None
    scan_name: str | None

    @classmethod
    def from_model(cls, *, certificate: ExpertCertificate) -> "ExpertCertificateResponse":
        """Подготовить сведения об удостоверении."""

        return cls(
            id=certificate.id,
            area_code=certificate.area_code,
            object_code=certificate.object_code,
            category=certificate.category,
            valid_until=certificate.valid_until,
            number=certificate.number,
            scan_name=certificate.scan_name,
        )
