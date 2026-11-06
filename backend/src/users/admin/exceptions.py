"""Ошибки управления аккаунтами."""


class ExpertHasActivityError(Exception):
    """Аккаунт связан с заявками или платежами."""


class CustomerNotFoundError(Exception):
    """Заказчик не найден."""


class CustomerHasActivityError(Exception):
    """У заказчика есть заявки или платежи."""
