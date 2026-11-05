"""Ошибки управления аккаунтами."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.users.admin.exceptions import ExpertHasActivityError


async def expert_has_activity(
    request: Request,
    error: ExpertHasActivityError,
) -> JSONResponse:
    """Сообщить о сохранении истории работ."""

    return JSONResponse(
        status_code=409,
        content={"detail": "Нельзя удалить эксперта, связанного с заявками или платежами"},
    )


def register_admin_user_error_handlers(*, app: FastAPI) -> None:
    """Подключить ошибки управления аккаунтами."""

    app.add_exception_handler(ExpertHasActivityError, expert_has_activity)
