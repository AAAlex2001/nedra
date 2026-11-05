"""Проверка доступа администратора."""

import secrets

from fastapi import Depends, Header, HTTPException

from src.core.settings import Settings, get_settings


def require_admin(
    *,
    x_admin_token: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> None:
    """Проверить токен администратора."""

    if not settings.admin_api_token:
        raise HTTPException(
            status_code=503,
            detail="Админ-доступ не настроен",
        )

    if x_admin_token is None:
        raise HTTPException(
            status_code=401,
            detail="Нет доступа",
        )

    if not secrets.compare_digest(
        x_admin_token.encode("utf-8"),
        settings.admin_api_token.encode("utf-8"),
    ):
        raise HTTPException(
            status_code=401,
            detail="Нет доступа",
        )
