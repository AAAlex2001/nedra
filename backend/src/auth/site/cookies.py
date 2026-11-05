"""Cookie авторизации."""

from fastapi import Response

from src.auth.options import AUTH_COOKIE, SECONDS_IN_DAY
from src.core.settings import Settings


def set_auth_cookie(
    *,
    response: Response,
    token: str,
    settings: Settings,
) -> None:
    """Сохранить токен в cookie."""

    response.set_cookie(
        key=AUTH_COOKIE,
        value=token,
        max_age=settings.jwt_expires_days * SECONDS_IN_DAY,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )


def clear_auth_cookie(
    *,
    response: Response,
    settings: Settings,
) -> None:
    """Удалить cookie авторизации."""

    response.delete_cookie(
        key=AUTH_COOKIE,
        path="/",
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
    )
