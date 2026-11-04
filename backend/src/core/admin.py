"""Защита административных маршрутов."""

import secrets

from fastapi import Header, HTTPException, status

from src.core.config import get_settings


def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    """Проверяет серверный токен администратора."""

    settings = get_settings()
    if not settings.admin_api_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Админский токен не настроен.",
        )
    if x_admin_token is None or not secrets.compare_digest(
        x_admin_token, settings.admin_api_token
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный админский токен.",
        )
