"""Вход в личный кабинет."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.auth.options import PASSWORD_MAX_BYTES


class LoginRequest(BaseModel):
    """Почта и пароль пользователя."""

    model_config = ConfigDict(hide_input_in_errors=True)

    email: EmailStr
    password: str = Field(
        max_length=PASSWORD_MAX_BYTES,
        repr=False,
    )
