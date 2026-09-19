"""Токены доступа в формате JWT.

Токен подписан секретом сервера, поэтому подделать его без секрета нельзя.
Внутри лежит id пользователя и срок годности. Сессий в БД нет: чтобы узнать,
кто пришёл, достаточно проверить подпись и прочитать id.
"""

from datetime import datetime, timedelta, timezone

import jwt

from app.config import get_settings

ALGORITHM = "HS256"


def create_access_token(user_id: int) -> str:
    """Выпустить токен для пользователя со сроком из настроек."""

    settings = get_settings()
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.jwt_expires_days)
    payload = {"sub": str(user_id), "exp": expires_at}

    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def read_user_id(token: str) -> int | None:
    """Достать id пользователя из токена. None — если токен испорчен или истёк."""

    settings = get_settings()

    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        return None

    subject = payload.get("sub")
    if subject is None:
        return None

    return int(subject)
