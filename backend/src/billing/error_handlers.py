"""Ответы на ошибки счетов."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.billing.exceptions import InvoiceAlreadyPaidError, InvoiceNotFoundError


async def invoice_not_found(
    request: Request,
    error: InvoiceNotFoundError,
) -> JSONResponse:
    """Сообщить об отсутствии счёта."""

    return JSONResponse(
        status_code=404,
        content={"detail": "Счёт не найден"},
    )


async def invoice_already_paid(
    request: Request,
    error: InvoiceAlreadyPaidError,
) -> JSONResponse:
    """Сообщить о подтверждённой оплате."""

    return JSONResponse(
        status_code=409,
        content={"detail": "Оплата счёта уже подтверждена"},
    )


def register_billing_error_handlers(*, app: FastAPI) -> None:
    """Подключить ошибки счетов."""

    app.add_exception_handler(InvoiceNotFoundError, invoice_not_found)
    app.add_exception_handler(InvoiceAlreadyPaidError, invoice_already_paid)
