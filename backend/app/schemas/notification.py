from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NotificationSchema(BaseModel):
    """Уведомление в кабинете."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    expertise_id: int | None
    text: str
    created_at: datetime
    read_at: datetime | None


class NotificationsReadSchema(BaseModel):
    """Какие уведомления отметить прочитанными: все или только по указанным заявкам."""

    expertise_ids: list[int] | None = Field(
        None, description="Если задано — читаем только уведомления по этим заявкам"
    )
