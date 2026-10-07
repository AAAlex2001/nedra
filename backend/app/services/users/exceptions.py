"""Ошибки бизнес-логики пользователей. Роутеры переводят их в HTTP-коды."""


class WeakPasswordError(ValueError):
    """Пароль не проходит требования к сложности."""


class InvalidPhoneError(ValueError):
    """Телефон не похож на настоящий номер."""


class EmailAlreadyTakenError(Exception):
    """На этот email уже зарегистрирован пользователь."""


class InvalidCredentialsError(Exception):
    """Неверная пара email и пароль. Что именно неверно — не сообщаем."""


class EmailChangeError(Exception):
    """Смена email не прошла: адрес тот же, кода нет, он истёк или неверный."""


class EmailCodeCooldownError(Exception):
    """Код на смену email уже отправлен и ещё действует: новый пока не шлём."""

    def __init__(self, seconds: int) -> None:
        self.seconds = seconds
        super().__init__(f"Новый код можно запросить через {seconds // 60}:{seconds % 60:02d}")
