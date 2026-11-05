"""Ошибки управления обращениями."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.requests.exceptions import ContactRequestNotFoundError


async def contact_request_not_found(
    request: Request,
    error: ContactRequestNotFoundError,
) -> JSONResponse:
    """Сообщить об отсутствии обращения."""

    return JSONResponse(
        status_code=404,
        content={"detail": "Обращение не найдено"},
    )


def register_admin_contact_request_error_handlers(*, app: FastAPI) -> None:
    """Подключить ошибки управления обращениями."""

    app.add_exception_handler(
        ContactRequestNotFoundError,
        contact_request_not_found,
    )
