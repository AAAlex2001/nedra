"""Данные для подготовки договора аудита."""

from dataclasses import dataclass
from datetime import datetime

from pydantic import ValidationError

from src.audit.exceptions import AuditStateError
from src.audit.models.audit import Audit
from src.audit.models.audit_application import AuditApplication
from src.audit.models.audit_company import AuditCompany
from src.contracts.contract_terms import ContractTerms
from src.contracts.customer_template_values import company_template_values
from src.contracts.enums import ContractKind
from src.contracts.executors import get_executor_requisites
from src.contracts.models.contract import Contract
from src.contracts.schemas.company import CompanyDetails
from src.core.settings import Settings
from src.users.models.user import User


@dataclass(kw_only=True)
class AuditContractDetails:
    """Условия договора и реквизиты заказчика."""

    audit: Audit  # Объект, стоимость и срок работы.
    contract: Contract | None  # Вид договора и дата подтверждения.
    company: AuditCompany | None  # Реквизиты организации или ИП.
    application: AuditApplication | None  # Анкета и название объекта.

    def to_contract_terms(
        self,
        *,
        customer: User,
        signed_at: datetime,
        settings: Settings,
    ) -> ContractTerms:
        """Проверить условия и реквизиты договора."""

        audit = self.audit
        contract = self.contract
        object_name = self.application.object_name if self.application else None
        price = audit.agreed_price

        if contract is None or contract.kind is None:
            raise AuditStateError("Вид договора ещё не определён")

        if not object_name:
            raise AuditStateError("В заявке нет наименования объекта")

        if price is None:
            raise AuditStateError("Стоимость работы не согласована")

        try:
            if self.company is not None:
                company = CompanyDetails.model_validate(self.company, from_attributes=True)
                customer_values = company_template_values(company, customer)
            else:
                raise AuditStateError("В заявке нет реквизитов заказчика")
        except ValidationError as error:
            raise AuditStateError("Уточните реквизиты заказчика для договора") from error

        requisites = get_executor_requisites(
            kind=contract.kind,
            settings=settings,
        )

        return ContractTerms(
            number=f"БА-{signed_at.year}-{audit.id:04d}",
            signed_at=signed_at,
            kind=ContractKind(contract.kind),
            object_name=object_name,
            price=price,
            deadline=None,
            vat_rate=requisites.vat_rate,
            customer_values=customer_values,
        )
