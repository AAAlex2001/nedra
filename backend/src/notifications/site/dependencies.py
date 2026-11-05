"""Зависимости уведомлений."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.notifications.repositories.notifications import NotificationRepository
from src.notifications.site.usecases.list_notifications import ListNotificationsUseCase
from src.notifications.site.usecases.read_all_notifications import ReadAllNotificationsUseCase
from src.notifications.site.usecases.read_notification import ReadNotificationUseCase


def get_list_notifications_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> ListNotificationsUseCase:
    """Просмотр уведомлений."""

    return ListNotificationsUseCase(notifications=NotificationRepository(session=session))


def get_read_notification_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> ReadNotificationUseCase:
    """Прочтение уведомления."""

    return ReadNotificationUseCase(
        session=session,
        notifications=NotificationRepository(session=session),
    )


def get_read_all_notifications_usecase(
    *,
    session: AsyncSession = Depends(get_session),
) -> ReadAllNotificationsUseCase:
    """Прочтение всех уведомлений."""

    return ReadAllNotificationsUseCase(
        session=session,
        notifications=NotificationRepository(session=session),
    )
