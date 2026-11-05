"""Ошибки изменения тарифов."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.tariffs.admin.exceptions import InvalidTariffError


async def invalid_tariff(
    request: Request,
    error: InvalidTariffError,
) -> JSONResponse:
    """Сообщить о недопустимом тарифе."""

    return JSONResponse(
        status_code=422,
        content={"detail": str(error)},
    )


def register_admin_tariff_error_handlers(*, app: FastAPI) -> None:
    """Подключить ошибки тарифов."""

    app.add_exception_handler(InvalidTariffError, invalid_tariff)
