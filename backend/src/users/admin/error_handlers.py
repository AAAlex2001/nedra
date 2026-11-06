"""Ошибки управления аккаунтами."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.users.admin.exceptions import (
    CustomerHasActivityError,
    CustomerNotFoundError,
    ExpertHasActivityError,
)


async def expert_has_activity(
    request: Request,
    error: ExpertHasActivityError,
) -> JSONResponse:
    """Сообщить о сохранении истории работ."""

    return JSONResponse(
        status_code=409,
        content={"detail": "Нельзя удалить эксперта, связанного с заявками или платежами"},
    )


async def customer_not_found(
    request: Request,
    error: CustomerNotFoundError,
) -> JSONResponse:
    """Сообщить об отсутствии заказчика."""

    return JSONResponse(status_code=404, content={"detail": "Заказчик не найден"})


async def customer_has_activity(
    request: Request,
    error: CustomerHasActivityError,
) -> JSONResponse:
    """Сообщить о сохранении истории заказчика."""

    return JSONResponse(
        status_code=409,
        content={"detail": "Нельзя удалить заказчика, связанного с заявками или платежами"},
    )


def register_admin_user_error_handlers(*, app: FastAPI) -> None:
    """Подключить ошибки управления аккаунтами."""

    app.add_exception_handler(ExpertHasActivityError, expert_has_activity)
    app.add_exception_handler(CustomerNotFoundError, customer_not_found)
    app.add_exception_handler(CustomerHasActivityError, customer_has_activity)
