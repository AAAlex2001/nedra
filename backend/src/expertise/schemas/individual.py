"""Паспортные данные заказчика."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.expertise.models.expertise_individual import ExpertiseIndividual


class IndividualDetails(BaseModel):
    """Данные физического лица для договора."""

    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str = Field(
        min_length=3,
        max_length=255,
    )
    passport_number: str = Field(
        min_length=10,
        max_length=20,
    )
    passport_issued_by: str = Field(
        min_length=5,
        max_length=500,
    )
    passport_issued_at: date
    address: str = Field(
        min_length=5,
        max_length=500,
    )

    @field_validator("passport_number")
    @classmethod
    def normalize_passport_number(cls, value: str) -> str:
        """Отделить серию паспорта от номера."""

        digits = "".join(value.split())

        if len(digits) != 10 or not digits.isascii() or not digits.isdigit():
            raise ValueError("Серия и номер паспорта — 10 цифр")

        return f"{digits[:4]} {digits[4:]}"


class IndividualResponse(BaseModel):
    """Сохранённые реквизиты физического лица."""

    full_name: str
    passport_number: str
    passport_issued_by: str
    passport_issued_at: date
    address: str

    @classmethod
    def from_model(cls, *, individual: ExpertiseIndividual) -> "IndividualResponse":
        """Подготовить реквизиты заказчика."""

        return cls(
            full_name=individual.full_name,
            passport_number=individual.passport_number,
            passport_issued_by=individual.passport_issued_by,
            passport_issued_at=individual.passport_issued_at,
            address=individual.address,
        )
