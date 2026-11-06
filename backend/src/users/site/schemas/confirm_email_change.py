"""Подтверждение новой почты."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from src.users.enums import UserRole
from src.users.models.user import User


class EmailConfirmationRequest(BaseModel):
    """Код подтверждения из письма."""

    code: str = Field(
        pattern=r"^\s*[0-9]{6}\s*$",
        repr=False,
    )


class EmailConfirmationResponse(BaseModel):
    """Профиль текущего пользователя."""

    id: int
    email: EmailStr
    full_name: str
    phone: str
    role: UserRole
    created_at: datetime

    @classmethod
    def from_model(cls, *, user: User) -> "EmailConfirmationResponse":
        """Подготовить данные профиля."""

        return cls(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            role=UserRole(user.role),
            created_at=user.created_at,
        )
