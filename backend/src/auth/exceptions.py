"""Ошибки регистрации и входа."""


class InvalidCredentialsError(Exception):
    """Неверная почта или пароль."""


class WeakPasswordError(Exception):
    """Пароль не соответствует требованиям."""


class ExpertApplicationPendingError(Exception):
    """Заявка эксперта ещё рассматривается."""


class ExpertApplicationAlreadyPendingError(Exception):
    """Заявка с этой почтой уже рассматривается."""
