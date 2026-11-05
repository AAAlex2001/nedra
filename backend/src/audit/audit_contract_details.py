"""Данные для подготовки договора аудита."""

from dataclasses import dataclass

from src.audit.models.audit import Audit
from src.audit.models.audit_application import AuditApplication
from src.audit.models.audit_company import AuditCompany
from src.contracts.models.contract import Contract


@dataclass(kw_only=True)
class AuditContractDetails:
    """Условия договора и реквизиты заказчика."""

    audit: Audit  # Объект, стоимость и срок работы.
    contract: Contract | None  # Вид договора и дата подтверждения.
    company: AuditCompany | None  # Реквизиты организации или ИП.
    application: AuditApplication | None  # Анкета и название объекта.
