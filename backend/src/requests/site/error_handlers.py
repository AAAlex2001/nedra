"""Ошибки подачи обращения."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.requests.exceptions import UnknownActivityError


async def unknown_activity(
    request: Request,
    error: UnknownActivityError,
) -> JSONResponse:
    """Сообщить о неизвестной услуге."""

    return JSONResponse(
        status_code=422,
        content={"detail": str(error)},
    )


def register_contact_request_error_handlers(*, app: FastAPI) -> None:
    """Подключить ошибки обращения."""

    app.add_exception_handler(UnknownActivityError, unknown_activity)
