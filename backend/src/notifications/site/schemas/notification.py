"""Уведомления личного кабинета."""

from datetime import datetime

from pydantic import BaseModel

from src.notifications.models.notification import Notification


class NotificationResponse(BaseModel):
    """Текст и состояние уведомления."""

    id: int
    expertise_id: int | None
    audit_id: int | None
    kind: str | None
    text: str
    created_at: datetime
    read_at: datetime | None

    @classmethod
    def from_model(cls, *, notification: Notification) -> "NotificationResponse":
        """Подготовить уведомление для кабинета."""

        return cls(
            id=notification.id,
            expertise_id=notification.expertise_id,
            audit_id=notification.audit_id,
            kind=notification.kind,
            text=notification.text,
            created_at=notification.created_at,
            read_at=notification.read_at,
        )
