"""Список аудитов."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from src.audit.enums import AuditStatus
from src.audit.models.audit import Audit


class AuditListItemResponse(BaseModel):
    """Краткие сведения для списка."""

    id: int
    customer_id: int
    lead_id: int | None
    status: AuditStatus
    price: Decimal | None
    created_at: datetime

    @classmethod
    def from_model(cls, *, audit: Audit) -> "AuditListItemResponse":
        """Подготовить строку списка."""

        return cls(
            id=audit.id,
            customer_id=audit.customer_id,
            lead_id=audit.lead_id,
            status=audit.status,
            price=audit.agreed_price if audit.agreed_price is not None else audit.customer_budget,
            created_at=audit.created_at,
        )
