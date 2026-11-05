"""Данные пользователя."""

from datetime import datetime

from pydantic import BaseModel, EmailStr

from src.users.enums import UserRole
from src.users.models.user import User


class UserResponse(BaseModel):
    """Профиль текущего пользователя."""

    id: int
    email: EmailStr
    full_name: str
    phone: str
    role: UserRole
    created_at: datetime

    @classmethod
    def from_model(cls, *, user: User) -> "UserResponse":
        """Подготовить данные профиля."""

        return cls(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            role=UserRole(user.role),
            created_at=user.created_at,
        )
