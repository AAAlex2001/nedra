"""Создание аккаунта заказчика."""

import asyncio

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.passwords import hash_password
from src.auth.site.schemas.register import RegisterRequest
from src.users.contact_validation import normalize_email, normalize_phone
from src.users.enums import UserRole
from src.users.exceptions import EmailAlreadyTakenError
from src.users.models.user import User
from src.users.repositories.users import UserRepository
from src.users.site.schemas.user import UserResponse


class RegisterUserUseCase:
    """Регистрация заказчика."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        users: UserRepository,
    ) -> None:
        """Сессия и пользователи."""

        self.session = session
        self.users = users

    async def execute(self, *, payload: RegisterRequest) -> UserResponse:
        """Создать аккаунт заказчика."""

        email = normalize_email(email=payload.email)
        phone = normalize_phone(phone=payload.phone)

        if await self.users.get_by_email(email=email) is not None:
            raise EmailAlreadyTakenError()

        password_hash = await asyncio.to_thread(
            hash_password,
            password=payload.password,
        )
        user = User(
            email=email,
            password_hash=password_hash,
            full_name=payload.full_name.strip(),
            phone=phone,
            role=UserRole.CUSTOMER,
        )

        try:
            await self.users.add(user=user)
            response = UserResponse.from_model(user=user)
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()

            if await self.users.get_by_email(email=email) is not None:
                raise EmailAlreadyTakenError() from None

            raise

        return response
