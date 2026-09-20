"""Проверка реквизитов организации заказчика."""

from app.services.billing.exceptions import InvalidCompanyError

INN_LENGTHS = (10, 12)
KPP_LENGTH = 9


def normalize_inn(inn: str) -> str:
    """ИНН из цифр: 10 знаков у организации, 12 у предпринимателя."""

    digits = "".join(char for char in inn if char.isdigit())

    if len(digits) not in INN_LENGTHS:
        raise InvalidCompanyError("ИНН должен состоять из 10 или 12 цифр")

    return digits


def normalize_kpp(kpp: str | None) -> str | None:
    """КПП из девяти цифр. У предпринимателя его нет, поэтому пустое значение допустимо."""

    if not kpp or not kpp.strip():
        return None

    digits = "".join(char for char in kpp if char.isdigit())

    if len(digits) != KPP_LENGTH:
        raise InvalidCompanyError("КПП должен состоять из 9 цифр")

    return digits
