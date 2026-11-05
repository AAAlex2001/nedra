"""Условия договора по заявке."""

from datetime import datetime

from pydantic import ValidationError

from src.contracts.contract_terms import ContractTerms
from src.contracts.customer_template_values import (
    company_template_values,
    individual_template_values,
)
from src.contracts.enums import ContractKind
from src.contracts.executors import get_executor_requisites
from src.contracts.schemas.company import CompanyDetails
from src.core.settings import Settings
from src.expertise.exceptions import ExpertiseStateError
from src.expertise.expertise_contract_details import ExpertiseContractDetails
from src.expertise.schemas.individual import IndividualDetails
from src.users.models.user import User


def prepare_expertise_contract(
    *,
    details: ExpertiseContractDetails,
    customer: User,
    signed_at: datetime,
    settings: Settings,
) -> ContractTerms:
    """Проверить условия и реквизиты договора."""

    expertise = details.expertise
    contract = details.contract
    object_name = expertise.object_name
    price = expertise.price

    if contract is None or contract.kind is None:
        raise ExpertiseStateError("Вид договора ещё не определён")

    if not object_name:
        raise ExpertiseStateError("В заявке нет наименования объекта")

    if price is None:
        raise ExpertiseStateError("Стоимость работы не согласована")

    try:
        if details.company is not None:
            company = CompanyDetails.model_validate(details.company, from_attributes=True)
            customer_values = company_template_values(company, customer)
        elif details.individual is not None:
            individual = IndividualDetails.model_validate(details.individual, from_attributes=True)
            customer_values = individual_template_values(individual, customer)
        else:
            raise ExpertiseStateError("В заявке нет реквизитов заказчика")
    except ValidationError as error:
        raise ExpertiseStateError("Уточните реквизиты заказчика для договора") from error

    requisites = get_executor_requisites(
        kind=contract.kind,
        settings=settings,
    )

    return ContractTerms(
        number=f"БЭ-{signed_at.year}-{expertise.id:04d}",
        signed_at=signed_at,
        kind=ContractKind(contract.kind),
        object_name=object_name,
        price=price,
        deadline=expertise.deadline,
        vat_rate=requisites.vat_rate,
        customer_values=customer_values,
    )
