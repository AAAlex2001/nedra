"""Данные кандидата в комиссию."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.commission.models.commission_application import CommissionApplication


class CandidateAttestation(BaseModel):
    """Аттестация кандидата."""

    area_code: str = Field(max_length=8)
    object_code: str = Field(max_length=8)
    category: int = Field(
        ge=1,
        le=3,
    )


class CreateCommissionApplicationRequest(BaseModel):
    """Новая заявка кандидата."""

    full_name: str = Field(
        min_length=3,
        max_length=255,
    )
    phone: str = Field(
        min_length=5,
        max_length=32,
    )
    email: EmailStr
    attestations: list[CandidateAttestation] = Field(
        min_length=1,
        max_length=30,
    )

    @field_validator(
        "full_name",
        "phone",
        mode="before",
    )
    @classmethod
    def strip_contact_spaces(cls, contact: object) -> object:
        """Убрать пробелы вокруг контакта."""

        return contact.strip() if isinstance(contact, str) else contact


class CommissionApplicationResponse(BaseModel):
    """Сохранённая заявка кандидата."""

    full_name: str = Field(
        min_length=3,
        max_length=255,
    )
    phone: str = Field(
        min_length=5,
        max_length=32,
    )
    email: EmailStr
    attestations: list[CandidateAttestation] = Field(
        min_length=1,
        max_length=30,
    )
    id: int
    created_at: datetime

    @field_validator(
        "full_name",
        "phone",
        mode="before",
    )
    @classmethod
    def strip_contact_spaces(cls, contact: object) -> object:
        """Убрать пробелы вокруг контакта."""

        return contact.strip() if isinstance(contact, str) else contact

    @classmethod
    def from_model(cls, *, application: CommissionApplication) -> "CommissionApplicationResponse":
        """Подготовить данные заявки."""

        return cls(
            id=application.id,
            full_name=application.full_name,
            phone=application.phone,
            email=application.email,
            attestations=[
                CandidateAttestation(**attestation) for attestation in application.attestations
            ],
            created_at=application.created_at,
        )
