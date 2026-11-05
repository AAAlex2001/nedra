"""Изменение профиля."""

from pydantic import BaseModel, Field, field_validator


class UpdateProfileRequest(BaseModel):
    """Новые имя и телефон."""

    full_name: str = Field(
        min_length=2,
        max_length=255,
    )
    phone: str = Field(
        min_length=10,
        max_length=32,
    )

    @field_validator(
        "full_name",
        mode="before",
    )
    @classmethod
    def strip_full_name(cls, full_name: object) -> object:
        """Убрать пробелы вокруг имени."""

        return full_name.strip() if isinstance(full_name, str) else full_name
