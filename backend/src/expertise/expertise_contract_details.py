"""Данные для подготовки договора экспертизы."""

from dataclasses import dataclass

from src.contracts.models.contract import Contract
from src.expertise.models.expertise import Expertise
from src.expertise.models.expertise_company import ExpertiseCompany
from src.expertise.models.expertise_individual import ExpertiseIndividual


@dataclass(kw_only=True)
class ExpertiseContractDetails:
    """Условия договора и реквизиты заказчика."""

    expertise: Expertise  # Объект, стоимость и срок работы.
    contract: Contract | None  # Вид договора и дата подтверждения.
    company: ExpertiseCompany | None  # Реквизиты организации или ИП.
    individual: ExpertiseIndividual | None  # Реквизиты физлица.
