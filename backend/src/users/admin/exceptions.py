"""Ошибки управления аккаунтами."""


class ExpertHasActivityError(Exception):
    """Аккаунт связан с заявками или платежами."""
