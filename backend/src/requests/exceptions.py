"""Ошибки обращений."""


class UnknownActivityError(Exception):
    """Услуги нет в справочнике."""


class ContactRequestNotFoundError(Exception):
    """Обращение не найдено."""
