"""Вход и регистрация."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repositories.expert_applications import ExpertApplicationRepository
from src.auth.site.usecases.login import LoginUserUseCase
from src.auth.site.usecases.register import RegisterUserUseCase
from src.core.database import get_session
from src.users.repositories.users import UserRepository


def get_login_usecase(*, session: AsyncSession = Depends(get_session)) -> LoginUserUseCase:
    """Вход в личный кабинет."""

    return LoginUserUseCase(
        users=UserRepository(session=session),
        applications=ExpertApplicationRepository(session=session),
    )


def get_register_usecase(*, session: AsyncSession = Depends(get_session)) -> RegisterUserUseCase:
    """Регистрация заказчика."""

    return RegisterUserUseCase(
        session=session,
        users=UserRepository(session=session),
    )
