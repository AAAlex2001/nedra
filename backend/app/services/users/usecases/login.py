"""Сценарий входа по email и паролю."""

import asyncio

from app.models.user import User
from app.schemas.user import LoginSchema
from app.services.users.exceptions import InvalidCredentialsError
from app.services.security.passwords import verify_password
from app.services.users.repo import UserRepository
from app.services.users.validators import normalize_email


class LoginUserUseCase:
    """Найти пользователя по email и сверить пароль с хешем."""

    def __init__(self, users: UserRepository) -> None:
        self.users = users

    async def execute(self, payload: LoginSchema) -> User:
        """Вернуть пользователя, если пара email и пароль верна. Иначе InvalidCredentialsError.

        На несуществующий email и на неверный пароль отвечаем одинаково,
        чтобы по ответу нельзя было узнать, зарегистрирован ли адрес.
        """

        email = normalize_email(payload.email)

        user = await self.users.get_by_email(email)
        if user is None:
            raise InvalidCredentialsError("Неверный email или пароль")

        password_matches = await asyncio.to_thread(
            verify_password, payload.password, user.password_hash
        )
        if not password_matches:
            raise InvalidCredentialsError("Неверный email или пароль")

        return user
