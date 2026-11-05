"""Ошибки профиля пользователя."""


class UserNotFoundError(Exception):
    """Пользователь не найден."""


class EmailAlreadyTakenError(Exception):
    """Почта уже занята."""


class InvalidPhoneError(Exception):
    """Некорректный номер телефона."""


class InvalidCertificateError(Exception):
    """Некорректные сведения об удостоверении."""


class InvalidDirectionError(Exception):
    """Неизвестное или повторное направление работы."""


class ExpertNotFoundError(Exception):
    """Профиль эксперта не найден."""


class CertificateNotFoundError(Exception):
    """Удостоверение эксперта не найдено."""


class EmailChangeError(Exception):
    """Не удалось подтвердить новый адрес."""


class EmailCodeDeliveryError(Exception):
    """Не удалось отправить код."""


class EmailCodeCooldownError(Exception):
    """Повторная отправка кода пока недоступна."""

    def __init__(self, *, seconds: int) -> None:
        """Время до повторной отправки."""

        self.seconds = seconds
        super().__init__("Дождитесь повторной отправки кода")
