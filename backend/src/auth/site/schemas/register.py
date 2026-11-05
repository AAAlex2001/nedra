"""Регистрация заказчика."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from src.auth.options import PASSWORD_MAX_BYTES, PASSWORD_MIN_LENGTH


class RegisterRequest(BaseModel):
    """Данные нового заказчика."""

    model_config = ConfigDict(hide_input_in_errors=True)

    email: EmailStr
    password: str = Field(
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_BYTES,
        repr=False,
    )
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
