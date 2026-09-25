"""Проверка реквизитов организации заказчика."""

from app.services.billing.exceptions import InvalidCompanyError

INN_LENGTHS = (10, 12)
KPP_LENGTH = 9
OGRN_LENGTHS = (13, 15)
BIC_LENGTH = 9
ACCOUNT_LENGTH = 20


def only_digits(value: str) -> str:
    """Оставить в строке только цифры: пробелы и дефисы в реквизитах не важны."""

    return "".join(char for char in value if char.isdigit())


def normalize_ogrn(ogrn: str) -> str:
    """ОГРН из 13 цифр у организации или ОГРНИП из 15 у предпринимателя."""

    digits = only_digits(ogrn)

    if len(digits) not in OGRN_LENGTHS:
        raise InvalidCompanyError("ОГРН должен состоять из 13 или 15 цифр")

    return digits


def normalize_bic(bic: str) -> str:
    """БИК банка из девяти цифр."""

    digits = only_digits(bic)

    if len(digits) != BIC_LENGTH:
        raise InvalidCompanyError("БИК должен состоять из 9 цифр")

    return digits


def normalize_account(account: str, title: str) -> str:
    """Расчётный или корреспондентский счёт из 20 цифр."""

    digits = only_digits(account)

    if len(digits) != ACCOUNT_LENGTH:
        raise InvalidCompanyError(f"{title} должен состоять из 20 цифр")

    return digits


def normalize_inn(inn: str) -> str:
    """ИНН из цифр: 10 знаков у организации, 12 у предпринимателя."""

    digits = only_digits(inn)

    if len(digits) not in INN_LENGTHS:
        raise InvalidCompanyError("ИНН должен состоять из 10 или 12 цифр")

    return digits


def normalize_kpp(kpp: str | None) -> str | None:
    """КПП из девяти цифр. У предпринимателя его нет, поэтому пустое значение допустимо."""

    if not kpp or not kpp.strip():
        return None

    digits = only_digits(kpp)

    if len(digits) != KPP_LENGTH:
        raise InvalidCompanyError("КПП должен состоять из 9 цифр")

    return digits
