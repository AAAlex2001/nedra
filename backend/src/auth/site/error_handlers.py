"""HTTP-ответы на ошибки авторизации."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.auth.exceptions import (
    ExpertApplicationAlreadyPendingError,
    ExpertApplicationPendingError,
    InvalidCredentialsError,
    WeakPasswordError,
)


async def handle_invalid_credentials(
    request: Request,
    error: InvalidCredentialsError,
) -> JSONResponse:
    """Сообщить о неверных данных входа."""

    return JSONResponse(
        status_code=401,
        content={"detail": "Неверный email или пароль"},
    )


async def handle_pending_expert_application(
    request: Request,
    error: ExpertApplicationPendingError,
) -> JSONResponse:
    """Сообщить о рассмотрении заявки."""

    return JSONResponse(
        status_code=403,
        content={"detail": "Ваша заявка эксперта ещё на рассмотрении"},
    )


async def handle_weak_password(
    request: Request,
    error: WeakPasswordError,
) -> JSONResponse:
    """Сообщить о требованиях к паролю."""

    return JSONResponse(
        status_code=422,
        content={"detail": str(error)},
    )


async def handle_duplicate_expert_application(
    request: Request,
    error: ExpertApplicationAlreadyPendingError,
) -> JSONResponse:
    """Сообщить о повторной заявке."""

    return JSONResponse(
        status_code=409,
        content={"detail": "Заявка с этим email уже на рассмотрении"},
    )


def register_auth_error_handlers(*, app: FastAPI) -> None:
    """Подключить обработку ошибок входа."""

    app.add_exception_handler(InvalidCredentialsError, handle_invalid_credentials)
    app.add_exception_handler(
        ExpertApplicationPendingError,
        handle_pending_expert_application,
    )
    app.add_exception_handler(WeakPasswordError, handle_weak_password)
    app.add_exception_handler(
        ExpertApplicationAlreadyPendingError,
        handle_duplicate_expert_application,
    )
