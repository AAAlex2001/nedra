"""Пользователи: фабрики сценариев, cookie с токеном, текущий пользователь, роли."""

from fastapi import Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_session
from app.models.user import User, UserRole
from app.services.experts.repo import ExpertApplicationRepository
from app.services.security.tokens import read_user_id
from app.services.users.repo import UserRepository
from app.services.users.usecases.login import LoginUserUseCase
from app.services.users.usecases.register import RegisterUserUseCase

AUTH_COOKIE = "access_token"
SECONDS_IN_DAY = 60 * 60 * 24


def get_user_repository(
    session: AsyncSession = Depends(get_session),
) -> UserRepository:
    """Репозиторий пользователей с сессией текущего запроса."""

    return UserRepository(session)


def get_register_usecase(
    users: UserRepository = Depends(get_user_repository),
) -> RegisterUserUseCase:
    """Сценарий регистрации."""

    return RegisterUserUseCase(users)


def get_login_usecase(
    users: UserRepository = Depends(get_user_repository),
    session: AsyncSession = Depends(get_session),
) -> LoginUserUseCase:
    """Сценарий входа. Репозиторий заявок нужен, чтобы отличить ожидающего эксперта."""

    return LoginUserUseCase(users, ExpertApplicationRepository(session))


def set_auth_cookie(response: Response, token: str) -> None:
    """Положить токен в httponly-cookie: JavaScript её не видит, браузер шлёт сам."""

    settings = get_settings()

    response.set_cookie(
        AUTH_COOKIE,
        token,
        max_age=settings.jwt_expires_days * SECONDS_IN_DAY,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
        path="/",
    )


def clear_auth_cookie(response: Response) -> None:
    """Удалить cookie с токеном — это и есть выход из аккаунта."""

    response.delete_cookie(AUTH_COOKIE, path="/")


async def get_optional_user(
    request: Request,
    users: UserRepository = Depends(get_user_repository),
) -> User | None:
    """Пользователь по токену из cookie или None, если токена нет или он негодный."""

    token = request.cookies.get(AUTH_COOKIE)
    if token is None:
        return None

    user_id = read_user_id(token)
    if user_id is None:
        return None

    return await users.get_by_id(user_id)


async def get_current_user(
    user: User | None = Depends(get_optional_user),
) -> User:
    """Пользователь по токену из cookie. Без валидного токена — 401."""

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется вход",
        )

    return user


def check_role(user: User, role: UserRole) -> User:
    """Вернуть пользователя, если его активная роль совпадает, иначе 403."""

    if user.role != role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Действие доступно только для роли " + role,
        )

    return user


def require_customer(user: User = Depends(get_current_user)) -> User:
    """Пропустить только заказчика."""

    return check_role(user, UserRole.CUSTOMER)


def require_expert(user: User = Depends(get_current_user)) -> User:
    """Пропустить только эксперта."""

    return check_role(user, UserRole.EXPERT)
