"""Проверка и нормализация данных пользователя.

Pydantic проверяет форму (длина, формат email), а здесь — бизнес-правила,
которые сложно выразить в схеме: сложность пароля, вид телефона.
Функции чистые: не ходят в БД и не знают про HTTP.
"""

from app.services.users.exceptions import InvalidPhoneError, WeakPasswordError

PASSWORD_MIN_LENGTH = 8
PHONE_MIN_DIGITS = 10
PHONE_MAX_DIGITS = 15


def normalize_email(email: str) -> str:
    """Email в нижнем регистре без пробелов по краям, чтобы Ivan@mail.ru и ivan@mail.ru были одним человеком."""

    return email.strip().lower()


def validate_password(password: str) -> None:
    """Пароль не короче 8 символов и содержит хотя бы одну букву и одну цифру."""

    if len(password) < PASSWORD_MIN_LENGTH:
        raise WeakPasswordError(f"Пароль должен быть не короче {PASSWORD_MIN_LENGTH} символов")

    has_letter = any(char.isalpha() for char in password)
    has_digit = any(char.isdigit() for char in password)

    if not has_letter or not has_digit:
        raise WeakPasswordError("Пароль должен содержать хотя бы одну букву и одну цифру")


def normalize_phone(phone: str) -> str:
    """Оставить в телефоне только цифры и ведущий плюс. Пример: «+7 (999) 000-00-00» → «+79990000000»."""

    stripped = phone.strip()
    digits = "".join(char for char in stripped if char.isdigit())

    if len(digits) < PHONE_MIN_DIGITS or len(digits) > PHONE_MAX_DIGITS:
        raise InvalidPhoneError("Укажите телефон в формате +7 999 000-00-00")

    if stripped.startswith("+"):
        return "+" + digits

    return digits
