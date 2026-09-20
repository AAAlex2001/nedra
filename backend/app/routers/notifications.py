from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies.expertise import get_notification_repository
from app.dependencies.users import get_current_user
from app.models.user import User
from app.schemas.notification import NotificationSchema
from app.services.notifications.repo import NotificationRepository


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
async def list_notifications(
    limit: int = Query(50, ge=1, le=200),
    user: User = Depends(get_current_user),
    notifications: NotificationRepository = Depends(get_notification_repository),
) -> list[NotificationSchema]:
    """Уведомления текущего пользователя, новые первыми."""

    items = await notifications.list_for_user(user.id, limit)

    return [NotificationSchema.model_validate(item) for item in items]


@router.post("/read-all")
async def read_all_notifications(
    user: User = Depends(get_current_user),
    notifications: NotificationRepository = Depends(get_notification_repository),
) -> list[NotificationSchema]:
    """Отметить все уведомления прочитанными и вернуть обновлённый список."""

    await notifications.mark_all_read(user.id)
    items = await notifications.list_for_user(user.id, 50)

    return [NotificationSchema.model_validate(item) for item in items]


@router.post("/{notification_id}/read")
async def read_notification(
    notification_id: int,
    user: User = Depends(get_current_user),
    notifications: NotificationRepository = Depends(get_notification_repository),
) -> NotificationSchema:
    """Отметить уведомление прочитанным."""

    notification = await notifications.get_for_user(notification_id, user.id)
    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Уведомление не найдено",
        )

    updated = await notifications.mark_read(notification)

    return NotificationSchema.model_validate(updated)
