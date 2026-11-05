"""Подача заявки на аудит."""

from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from src.audit.options import MIN_AUDIT_PRICE
from src.audit.schemas.audit_details import AuditDetailsSchema
from src.contracts.enums import CustomerType
from src.contracts.schemas.company import CompanyDetails


class CreateAuditRequest(BaseModel):
    """Новая заявка на аудит."""

    details: AuditDetailsSchema
    price: Decimal | None = Field(
        default=None,
        ge=MIN_AUDIT_PRICE,
        max_digits=10,
        decimal_places=2,
    )
    customer_type: CustomerType = CustomerType.LEGAL
    company: CompanyDetails
    comment: str | None = Field(
        default=None,
        max_length=4000,
    )

    @model_validator(mode="after")
    def validate_customer_and_budget(self) -> "CreateAuditRequest":
        """Проверить заказчика и бюджет."""

        if self.customer_type not in (CustomerType.LEGAL, CustomerType.ENTREPRENEUR):
            raise ValueError("Аудит заказывает юридическое лицо или индивидуальный предприниматель")

        if self.details.budget.mode == "custom" and self.price is None:
            raise ValueError("Укажите сумму")

        if self.details.budget.mode == "none" and self.price is not None:
            raise ValueError("Бюджет не установлен: сумму не указывают")

        return self
