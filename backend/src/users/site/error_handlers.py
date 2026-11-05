"""HTTP-ответы на ошибки профиля."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.users.exceptions import (
    CertificateNotFoundError,
    EmailAlreadyTakenError,
    EmailChangeError,
    EmailCodeCooldownError,
    EmailCodeDeliveryError,
    ExpertNotFoundError,
    InvalidCertificateError,
    InvalidDirectionError,
    InvalidPhoneError,
    UserNotFoundError,
)


async def user_not_found(
    request: Request,
    error: UserNotFoundError,
) -> JSONResponse:
    """Сообщить об отсутствии пользователя."""

    return JSONResponse(
        status_code=404,
        content={"detail": "Пользователь не найден"},
    )


async def email_already_taken(
    request: Request,
    error: EmailAlreadyTakenError,
) -> JSONResponse:
    """Сообщить о занятом адресе."""

    return JSONResponse(
        status_code=409,
        content={"detail": "Этот email уже занят"},
    )


async def invalid_phone(
    request: Request,
    error: InvalidPhoneError,
) -> JSONResponse:
    """Сообщить о неверном телефоне."""

    return JSONResponse(
        status_code=422,
        content={"detail": str(error)},
    )


async def email_change_failed(
    request: Request,
    error: EmailChangeError,
) -> JSONResponse:
    """Сообщить об ошибке подтверждения."""

    return JSONResponse(
        status_code=422,
        content={"detail": str(error)},
    )


async def email_code_cooldown(
    request: Request,
    error: EmailCodeCooldownError,
) -> JSONResponse:
    """Сообщить время до повторной отправки."""

    return JSONResponse(
        status_code=429,
        content={"detail": str(error)},
        headers={"Retry-After": str(error.seconds)},
    )


async def email_code_delivery_failed(
    request: Request,
    error: EmailCodeDeliveryError,
) -> JSONResponse:
    """Сообщить о недоступности отправки писем."""

    return JSONResponse(
        status_code=503,
        content={"detail": "Не удалось отправить код. Повторите попытку позже"},
    )


async def invalid_attestation(
    request: Request,
    error: Exception,
) -> JSONResponse:
    """Сообщить об ошибке в сведениях эксперта."""

    return JSONResponse(
        status_code=422,
        content={"detail": str(error)},
    )


async def expert_not_found(
    request: Request,
    error: ExpertNotFoundError,
) -> JSONResponse:
    """Сообщить об отсутствии профиля эксперта."""

    return JSONResponse(
        status_code=404,
        content={"detail": "Профиль эксперта не найден"},
    )


async def certificate_not_found(
    request: Request,
    error: CertificateNotFoundError,
) -> JSONResponse:
    """Сообщить об отсутствии удостоверения."""

    return JSONResponse(
        status_code=404,
        content={"detail": "Удостоверение не найдено"},
    )


def register_user_error_handlers(*, app: FastAPI) -> None:
    """Подключить обработку ошибок профиля."""

    app.add_exception_handler(UserNotFoundError, user_not_found)
    app.add_exception_handler(EmailAlreadyTakenError, email_already_taken)
    app.add_exception_handler(InvalidPhoneError, invalid_phone)
    app.add_exception_handler(EmailChangeError, email_change_failed)
    app.add_exception_handler(EmailCodeCooldownError, email_code_cooldown)
    app.add_exception_handler(EmailCodeDeliveryError, email_code_delivery_failed)
    app.add_exception_handler(InvalidCertificateError, invalid_attestation)
    app.add_exception_handler(InvalidDirectionError, invalid_attestation)
    app.add_exception_handler(ExpertNotFoundError, expert_not_found)
    app.add_exception_handler(CertificateNotFoundError, certificate_not_found)
