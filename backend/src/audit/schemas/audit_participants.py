"""Заказчик аудита."""

from pydantic import BaseModel

from src.audit.schemas.audit_company import AuditCompanyResponse
from src.contracts.enums import CustomerType


class AuditCustomerResponse(BaseModel):
    """Заказчик и сохранённые реквизиты."""

    id: int  # Номер заказчика.
    full_name: str  # Имя заказчика.
    customer_type: CustomerType  # Организация или ИП.
    company: AuditCompanyResponse | None  # Реквизиты для договора.
