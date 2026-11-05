"""HTTP-ошибки рассмотрения заявок экспертов."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.auth.admin.exceptions import (
    ExpertApplicationAlreadyReviewedError,
    ExpertApplicationNotFoundError,
)


async def handle_reviewed_expert_application(
    request: Request,
    error: ExpertApplicationAlreadyReviewedError,
) -> JSONResponse:
    """Сообщить о рассмотренной заявке."""

    return JSONResponse(
        status_code=409,
        content={"detail": "Заявка уже рассмотрена"},
    )


async def handle_missing_expert_application(
    request: Request,
    error: ExpertApplicationNotFoundError,
) -> JSONResponse:
    """Сообщить об отсутствии заявки."""

    return JSONResponse(
        status_code=404,
        content={"detail": "Заявка не найдена"},
    )


def register_admin_auth_error_handlers(*, app: FastAPI) -> None:
    """Подключить ошибки рассмотрения заявок."""

    app.add_exception_handler(
        ExpertApplicationAlreadyReviewedError,
        handle_reviewed_expert_application,
    )
    app.add_exception_handler(
        ExpertApplicationNotFoundError,
        handle_missing_expert_application,
    )
