"""Список экспертиз."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from src.expertise.enums import ExpertiseStatus
from src.expertise.models.expertise import Expertise


class ExpertiseListItemResponse(BaseModel):
    """Краткие сведения для списка."""

    id: int
    customer_id: int
    expert_id: int | None
    status: ExpertiseStatus
    price: Decimal | None
    created_at: datetime

    @classmethod
    def from_model(cls, *, expertise: Expertise) -> "ExpertiseListItemResponse":
        """Подготовить строку списка."""

        return cls(
            id=expertise.id,
            customer_id=expertise.customer_id,
            expert_id=expertise.expert_id,
            status=expertise.status,
            price=expertise.price,
            created_at=expertise.created_at,
        )
