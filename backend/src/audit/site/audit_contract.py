"""Условия договора по заявке."""

from datetime import datetime

from pydantic import ValidationError

from src.audit.audit_contract_details import AuditContractDetails
from src.audit.exceptions import AuditStateError
from src.contracts.contract_terms import ContractTerms
from src.contracts.customer_template_values import company_template_values
from src.contracts.enums import ContractKind
from src.contracts.executors import get_executor_requisites
from src.contracts.schemas.company import CompanyDetails
from src.core.settings import Settings
from src.users.models.user import User


def prepare_audit_contract(
    *,
    details: AuditContractDetails,
    customer: User,
    signed_at: datetime,
    settings: Settings,
) -> ContractTerms:
    """Проверить условия и реквизиты договора."""

    audit = details.audit
    contract = details.contract
    object_name = details.application.object_name if details.application else None
    price = audit.agreed_price

    if contract is None or contract.kind is None:
        raise AuditStateError("Вид договора ещё не определён")

    if not object_name:
        raise AuditStateError("В заявке нет наименования объекта")

    if price is None:
        raise AuditStateError("Стоимость работы не согласована")

    try:
        if details.company is not None:
            company = CompanyDetails.model_validate(details.company, from_attributes=True)
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
