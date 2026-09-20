"""Ошибки бизнес-логики экспертов. Роутеры переводят их в HTTP-коды."""


class InvalidCertificateError(ValueError):
    """Удостоверение не соответствует справочнику: неизвестная область, объект или их сочетание."""


class InvalidDirectionError(ValueError):
    """Неизвестное направление работы."""


class ApplicationAlreadyPendingError(Exception):
    """На этот email уже есть заявка, которая ждёт проверки."""


class ApplicationPendingError(Exception):
    """Пользователь пытается войти, пока его заявка не рассмотрена."""


class ApplicationNotFoundError(LookupError):
    """Заявки с таким идентификатором нет."""


class ApplicationAlreadyReviewedError(Exception):
    """Заявка уже одобрена или отклонена, повторно решить нельзя."""


class CertificateNotFoundError(LookupError):
    """Удостоверения с таким идентификатором нет в этой заявке."""


class ExpertNotFoundError(LookupError):
    """У пользователя нет профиля эксперта."""


class ContactsRequiredError(ValueError):
    """В заявке должны быть имя, email, телефон и пароль будущего эксперта."""
