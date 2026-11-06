"""Уведомления пользователя."""

from fastapi import APIRouter, Depends, Query

from src.auth.site.dependencies.authentication import get_current_user
from src.notifications.options import DEFAULT_LIST_LIMIT, MAX_LIST_LIMIT
from src.notifications.site.dependencies.notifications import (
    get_list_notifications_usecase,
    get_read_all_notifications_usecase,
    get_read_notification_usecase,
)
from src.notifications.site.schemas.notification import NotificationResponse
from src.notifications.site.usecases.list_notifications import ListNotificationsUseCase
from src.notifications.site.usecases.read_all_notifications import (
    ReadAllNotificationsUseCase,
)
from src.notifications.site.usecases.read_notification import ReadNotificationUseCase
from src.users.models.user import User

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
)


@router.get("")
async def list_notifications(
    *,
    limit: int = Query(
        default=DEFAULT_LIST_LIMIT,
        ge=1,
        le=MAX_LIST_LIMIT,
    ),
    user: User = Depends(get_current_user),
    usecase: ListNotificationsUseCase = Depends(get_list_notifications_usecase),
) -> list[NotificationResponse]:
    """Получить свои уведомления."""

    return await usecase.execute(
        user_id=user.id,
        limit=limit,
    )


@router.post("/read-all")
async def read_all_notifications(
    *,
    user: User = Depends(get_current_user),
    usecase: ReadAllNotificationsUseCase = Depends(get_read_all_notifications_usecase),
) -> list[NotificationResponse]:
    """Отметить все уведомления прочитанными."""

    return await usecase.execute(user_id=user.id)


@router.post("/{notification_id}/read")
async def read_notification(
    *,
    notification_id: int,
    user: User = Depends(get_current_user),
    usecase: ReadNotificationUseCase = Depends(get_read_notification_usecase),
) -> NotificationResponse:
    """Отметить уведомление прочитанным."""

    return await usecase.execute(
        notification_id=notification_id,
        user_id=user.id,
    )
