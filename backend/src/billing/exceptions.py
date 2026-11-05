"""Ошибки работы со счетами."""


class InvoiceNotFoundError(Exception):
    """Счёт не найден."""


class InvoiceAlreadyPaidError(Exception):
    """Оплата счёта уже подтверждена."""
