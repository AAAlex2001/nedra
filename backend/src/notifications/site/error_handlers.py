"""HTTP-ответы на ошибки уведомлений."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.notifications.exceptions import NotificationNotFoundError


async def notification_not_found(
    request: Request,
    error: NotificationNotFoundError,
) -> JSONResponse:
    """Сообщить об отсутствии уведомления."""

    return JSONResponse(
        status_code=404,
        content={"detail": "Уведомление не найдено"},
    )


def register_notification_error_handlers(*, app: FastAPI) -> None:
    """Подключить обработку ошибок уведомлений."""

    app.add_exception_handler(NotificationNotFoundError, notification_not_found)
