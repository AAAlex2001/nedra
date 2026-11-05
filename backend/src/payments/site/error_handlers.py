"""HTTP-ответы на ошибки оплаты."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.payments.exceptions import (
    PaymentConfigurationError,
    PaymentGatewayError,
    PaymentNotFoundError,
    PaymentStateError,
)


async def missing_payment(
    request: Request,
    error: PaymentNotFoundError,
) -> JSONResponse:
    """Сообщить об отсутствии платежа."""

    return JSONResponse(
        status_code=404,
        content={"detail": "Платёж не найден"},
    )


async def unavailable_gateway(
    request: Request,
    error: PaymentGatewayError,
) -> JSONResponse:
    """Сообщить о недоступности провайдера."""

    return JSONResponse(
        status_code=502,
        content={"detail": "Платёжный сервис временно недоступен"},
    )


async def missing_configuration(
    request: Request,
    error: PaymentConfigurationError,
) -> JSONResponse:
    """Сообщить об отсутствии настроек."""

    return JSONResponse(
        status_code=503,
        content={"detail": "Оплата не настроена"},
    )


async def invalid_payment_state(
    request: Request,
    error: PaymentStateError,
) -> JSONResponse:
    """Сообщить о недоступном этапе оплаты."""

    return JSONResponse(
        status_code=409,
        content={"detail": str(error)},
    )


def register_payment_error_handlers(*, app: FastAPI) -> None:
    """Подключить ошибки оплаты."""

    app.add_exception_handler(PaymentNotFoundError, missing_payment)
    app.add_exception_handler(PaymentGatewayError, unavailable_gateway)
    app.add_exception_handler(PaymentConfigurationError, missing_configuration)
    app.add_exception_handler(PaymentStateError, invalid_payment_state)
