"""Базовые механизмы безопасности: пароли и JWT-токены."""

import asyncio
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from src.core.config import get_settings


def hash_password(*, password: str) -> str:
    """Хэширует пароль с помощью bcrypt."""

    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(*, password: str, password_hash: str) -> bool:
    """Проверяет пароль против сохранённого хэша."""

    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


async def hash_password_async(*, password: str) -> str:
    """Асинхронная обёртка для хэширования пароля."""

    return await asyncio.to_thread(hash_password, password=password)


async def verify_password_async(*, password: str, password_hash: str) -> bool:
    """Асинхронная обёртка для проверки пароля."""

    return await asyncio.to_thread(verify_password, password=password, password_hash=password_hash)


def create_access_token(*, user_id: int) -> str:
    """Создаёт JWT access-токен для пользователя."""

    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(days=settings.jwt_expires_days),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def read_user_id(*, token: str) -> int | None:
    """Извлекает идентификатор пользователя из токена или None."""

    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
    subject = payload.get("sub")
    if not isinstance(subject, str):
        return None
    try:
        return int(subject)
    except ValueError:
        return None
