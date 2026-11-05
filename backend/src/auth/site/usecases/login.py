"""Проверка почты и пароля."""

import asyncio

from src.auth.exceptions import ExpertApplicationPendingError, InvalidCredentialsError
from src.auth.passwords import verify_password
from src.auth.repositories.expert_applications import ExpertApplicationRepository
from src.auth.site.schemas.login import LoginRequest
from src.users.contact_validation import normalize_email
from src.users.repositories.users import UserRepository
from src.users.site.schemas.user import UserResponse


class LoginUserUseCase:
    """Вход в личный кабинет."""

    def __init__(
        self,
        *,
        users: UserRepository,
        applications: ExpertApplicationRepository,
    ) -> None:
        """Пользователи и заявки экспертов."""

        self.users = users
        self.applications = applications

    async def execute(self, *, payload: LoginRequest) -> UserResponse:
        """Проверить данные для входа."""

        email = normalize_email(email=payload.email)
        user = await self.users.get_by_email(email=email)

        if user is None:
            pending_application = await self.applications.get_pending_by_email(email=email)

            if pending_application is not None:
                password_is_correct = await asyncio.to_thread(
                    verify_password,
                    password=payload.password,
                    password_hash=pending_application.password_hash,
                )

                if password_is_correct:
                    raise ExpertApplicationPendingError()

            raise InvalidCredentialsError()

        password_is_correct = await asyncio.to_thread(
            verify_password,
            password=payload.password,
            password_hash=user.password_hash,
        )

        if not password_is_correct:
            raise InvalidCredentialsError()

        return UserResponse.from_model(user=user)
