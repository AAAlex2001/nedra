"""Предложение цены аудита."""

from decimal import Decimal

from pydantic import BaseModel, Field

from src.audit.options import MIN_AUDIT_PRICE


class ProposeAuditPriceRequest(BaseModel):
    """Стоимость, предложенная руководителем."""

    price: Decimal = Field(
        ge=MIN_AUDIT_PRICE,
        max_digits=10,
        decimal_places=2,
    )
