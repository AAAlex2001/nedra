"""Зависимости авторизации."""

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.options import AUTH_COOKIE
from src.auth.repositories.expert_applications import ExpertApplicationRepository
from src.auth.site.usecases.login import LoginUserUseCase
from src.auth.site.usecases.register import RegisterUserUseCase
from src.auth.tokens import read_user_id
from src.core.database import get_session
from src.core.settings import Settings, get_settings
from src.users.enums import UserRole
from src.users.models.user import User
from src.users.repositories.users import UserRepository


def get_register_usecase(*, session: AsyncSession = Depends(get_session)) -> RegisterUserUseCase:
    """Регистрация заказчика."""

    return RegisterUserUseCase(
        session=session,
        users=UserRepository(session=session),
    )


def get_login_usecase(*, session: AsyncSession = Depends(get_session)) -> LoginUserUseCase:
    """Вход в личный кабинет."""

    return LoginUserUseCase(
        users=UserRepository(session=session),
        applications=ExpertApplicationRepository(session=session),
    )


def get_authenticated_user_id(
    *,
    request: Request,
    settings: Settings = Depends(get_settings),
) -> int:
    """Номер пользователя из токена."""

    token = request.cookies.get(AUTH_COOKIE)
    user_id = (
        read_user_id(
            token=token,
            settings=settings,
        )
        if token
        else None
    )

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Требуется вход",
        )

    return user_id


async def get_current_user(
    *,
    user_id: int = Depends(get_authenticated_user_id),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Текущий пользователь."""

    users = UserRepository(session=session)
    user = await users.get_by_id(user_id=user_id)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Требуется вход",
        )

    return user


def require_customer(*, user: User = Depends(get_current_user)) -> User:
    """Проверить роль заказчика."""

    if user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=403,
            detail="Действие доступно заказчику",
        )

    return user


def require_expert(*, user: User = Depends(get_current_user)) -> User:
    """Проверить роль эксперта."""

    if user.role != UserRole.EXPERT:
        raise HTTPException(
            status_code=403,
            detail="Действие доступно эксперту",
        )

    return user
