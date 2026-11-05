"""Проверка контактных данных."""

from src.users.exceptions import InvalidPhoneError
from src.users.options import PHONE_MAX_DIGITS, PHONE_MIN_DIGITS


def normalize_email(*, email: str) -> str:
    """Привести почту к единому виду."""

    return email.strip().lower()


def normalize_phone(*, phone: str) -> str:
    """Убрать оформление номера телефона."""

    phone = phone.strip()
    digits = "".join(character for character in phone if character in "0123456789")

    if not PHONE_MIN_DIGITS <= len(digits) <= PHONE_MAX_DIGITS:
        raise InvalidPhoneError("Укажите телефон в формате +7 999 000-00-00")

    if phone.startswith("+"):
        return f"+{digits}"

    return digits
