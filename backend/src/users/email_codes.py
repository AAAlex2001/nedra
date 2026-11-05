"""Коды подтверждения почты."""

import hashlib
import secrets

from src.users.options import EMAIL_CODE_DIGITS


def create_email_code() -> str:
    """Создать случайный код."""

    return f"{secrets.randbelow(10 ** EMAIL_CODE_DIGITS):0{EMAIL_CODE_DIGITS}d}"


def hash_email_code(
    *,
    user_id: int,
    code: str,
) -> str:
    """Получить хеш кода пользователя."""

    return hashlib.sha256(f"{user_id}:{code}".encode("utf-8")).hexdigest()
