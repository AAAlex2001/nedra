"""Доменные исключения заявок."""


class UnknownActivityError(ValueError):
    """Неизвестный вид деятельности в заявке."""


class RequestNotFoundError(LookupError):
    """Заявка не найдена."""
