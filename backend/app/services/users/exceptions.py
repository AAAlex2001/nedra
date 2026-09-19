"""Ошибки бизнес-логики пользователей. Роутеры переводят их в HTTP-коды."""


class WeakPasswordError(ValueError):
    """Пароль не проходит требования к сложности."""


class InvalidPhoneError(ValueError):
    """Телефон не похож на настоящий номер."""


class EmailAlreadyTakenError(Exception):
    """На этот email уже зарегистрирован пользователь."""


class InvalidCredentialsError(Exception):
    """Неверная пара email и пароль. Что именно неверно — не сообщаем."""
