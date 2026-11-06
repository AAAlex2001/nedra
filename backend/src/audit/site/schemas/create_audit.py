"""Подача заявки на аудит."""

from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from src.audit.enums import AuditStatus
from src.audit.models.audit import Audit
from src.audit.options import MIN_AUDIT_PRICE, OBJECT_NAME_MAX_LENGTH
from src.audit.schemas.audit_conditions import AuditConditionsResponse
from src.audit.schemas.audit_dates import AuditDatesResponse
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

    def describe_objects(self) -> str:
        """Название объектов для списка заявок."""

        if self.details.scope == "all" and self.details.fleet is not None:
            object_name = (
                f"Все ОПО {self.details.applicant.organization} ({self.details.fleet.count})"
            )
        else:
            object_name = "; ".join(
                f"{audit_object.name} ({audit_object.reg_number})"
                for audit_object in self.details.objects
            )

        return object_name[:OBJECT_NAME_MAX_LENGTH]


class CreateAuditResponse(BaseModel):
    """Условия и состояние аудита."""

    id: int  # Номер аудита.
    customer_id: int  # Номер заказчика.
    lead_id: int | None  # Номер руководителя группы.
    status: AuditStatus  # Текущий этап.
    result: str | None  # Результат заключения.
    conditions: AuditConditionsResponse  # Цена и пожелания заказчика.
    dates: AuditDatesResponse  # Даты прохождения этапов.

    @classmethod
    def from_model(cls, *, audit: Audit) -> "CreateAuditResponse":
        """Подготовить сведения об аудите."""

        return cls(
            id=audit.id,
            customer_id=audit.customer_id,
            lead_id=audit.lead_id,
            status=audit.status,
            result=audit.result,
            conditions=AuditConditionsResponse.from_model(audit=audit),
            dates=AuditDatesResponse.from_model(audit=audit),
        )
