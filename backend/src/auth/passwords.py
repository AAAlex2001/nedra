"""Проверка и хеширование паролей."""

import bcrypt

from src.auth.exceptions import WeakPasswordError
from src.auth.options import PASSWORD_MAX_BYTES, PASSWORD_MIN_LENGTH


def validate_password(*, password: str) -> None:
    """Проверить требования к паролю."""

    if len(password) < PASSWORD_MIN_LENGTH:
        raise WeakPasswordError(f"Пароль должен быть не короче {PASSWORD_MIN_LENGTH} символов")

    if len(password.encode("utf-8")) > PASSWORD_MAX_BYTES:
        raise WeakPasswordError("Пароль слишком длинный: допустимо не более 72 байт UTF-8")

    has_letter = any(character.isalpha() for character in password)
    has_digit = any(character.isdigit() for character in password)

    if not has_letter or not has_digit:
        raise WeakPasswordError("Пароль должен содержать хотя бы одну букву и одну цифру")


def hash_password(*, password: str) -> str:
    """Создать хеш пароля."""

    validate_password(password=password)

    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")


def verify_password(
    *,
    password: str,
    password_hash: str,
) -> bool:
    """Сверить пароль с хешем."""

    if len(password.encode("utf-8")) > PASSWORD_MAX_BYTES:
        return False

    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except ValueError:
        return False
