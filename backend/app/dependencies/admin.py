"""Защита админских ручек серверным токеном."""

import secrets

from fastapi import Header, HTTPException, status

from app.config import get_settings


def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    """Пропустить запрос только с верным заголовком X-Admin-Token.

    Токен знает только сервер Next.js и добавляет его к запросам из админки.
    В браузер он не попадает. Сравнение через compare_digest — за постоянное
    время, чтобы по скорости ответа нельзя было подобрать токен посимвольно.
    """

    expected = get_settings().admin_api_token

    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Админ-доступ не настроен",
        )

    if not x_admin_token or not secrets.compare_digest(x_admin_token, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Нет доступа",
        )
