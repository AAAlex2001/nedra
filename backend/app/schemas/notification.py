from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationSchema(BaseModel):
    """Уведомление в кабинете."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    expertise_id: int | None
    kind: str | None = None
    text: str
    created_at: datetime
    read_at: datetime | None
