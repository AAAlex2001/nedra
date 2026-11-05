"""Ошибки управления заявками кандидатов."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.commission.admin.exceptions import CommissionApplicationNotFoundError


async def commission_application_not_found(
    request: Request,
    error: CommissionApplicationNotFoundError,
) -> JSONResponse:
    """Сообщить об отсутствии заявки."""

    return JSONResponse(
        status_code=404,
        content={"detail": "Заявка кандидата не найдена"},
    )


def register_admin_commission_error_handlers(*, app: FastAPI) -> None:
    """Подключить ошибки управления заявками."""

    app.add_exception_handler(
        CommissionApplicationNotFoundError,
        commission_application_not_found,
    )
