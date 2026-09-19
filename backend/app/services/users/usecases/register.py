"""Сценарий регистрации нового пользователя."""

import asyncio

from app.models.user import User
from app.schemas.user import RegisterSchema
from app.services.users.exceptions import EmailAlreadyTakenError
from app.services.security.passwords import hash_password
from app.services.users.repo import UserRepository
from app.services.users.validators import (
    normalize_email,
    normalize_phone,
    validate_password,
)


class RegisterUserUseCase:
    """Проверить данные, убедиться, что email свободен, захешировать пароль и сохранить."""

    def __init__(self, users: UserRepository) -> None:
        self.users = users

    async def execute(self, payload: RegisterSchema) -> User:
        """Создать пользователя. Бросает WeakPasswordError, InvalidPhoneError, EmailAlreadyTakenError."""

        email = normalize_email(payload.email)
        phone = normalize_phone(payload.phone)
        validate_password(payload.password)

        existing = await self.users.get_by_email(email)
        if existing is not None:
            raise EmailAlreadyTakenError(f"Email {email} уже занят")

        password_hash = await asyncio.to_thread(hash_password, payload.password)

        user = User(
            email=email,
            password_hash=password_hash,
            full_name=payload.full_name.strip(),
            phone=phone,
            role=payload.role,
        )

        return await self.users.add(user)
