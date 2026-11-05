"""Токены доступа."""

from datetime import UTC, datetime, timedelta

import jwt

from src.auth.options import JWT_ALGORITHM, MAX_USER_ID
from src.core.settings import Settings


def create_access_token(
    *,
    user_id: int,
    settings: Settings,
) -> str:
    """Выпустить токен пользователя."""

    expires_at = datetime.now(UTC) + timedelta(days=settings.jwt_expires_days)

    return jwt.encode(
        {"sub": str(user_id), "exp": expires_at},
        settings.jwt_secret,
        algorithm=JWT_ALGORITHM,
    )


def read_user_id(
    *,
    token: str,
    settings: Settings,
) -> int | None:
    """Проверить токен и получить номер пользователя."""

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "exp"]},
        )
        subject = payload["sub"]

        if not isinstance(subject, str) or not subject.isascii() or not subject.isdecimal():
            return None

        user_id = int(subject)
    except (jwt.InvalidTokenError, ValueError, TypeError, OverflowError):
        return None

    if not 1 <= user_id <= MAX_USER_ID:
        return None

    return user_id
