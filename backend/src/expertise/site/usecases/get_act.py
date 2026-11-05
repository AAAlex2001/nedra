"""Скачивание акта выполненных работ."""

import asyncio

from src.billing.act_data import ActData, ActPayer
from src.billing.documents.act_pdf import build_act_pdf
from src.contracts.executors import get_executor_requisites
from src.contracts.repositories.contracts import ContractRepository
from src.core.settings import Settings
from src.documents.generated_document import GeneratedDocument
from src.expertise.enums import ExpertiseStatus
from src.expertise.exceptions import ExpertiseNotFoundError, ExpertiseStateError
from src.expertise.repositories.expertise_customers import ExpertiseCustomerRepository
from src.expertise.repositories.expertises import ExpertiseRepository
from src.users.enums import UserRole
from src.users.models.user import User


class GetExpertiseActUseCase:
    """Акт по принятой заказчиком работе."""

    def __init__(
        self,
        *,
        expertises: ExpertiseRepository,
        customers: ExpertiseCustomerRepository,
        contracts: ContractRepository,
        settings: Settings,
    ) -> None:
        """Работы, реквизиты и договоры."""

        self.expertises = expertises
        self.customers = customers
        self.contracts = contracts
        self.settings = settings

    async def execute(
        self,
        *,
        expertise_id: int,
        user: User,
    ) -> GeneratedDocument:
        """Создать акт выполненных работ."""

        expertise = await self.expertises.get_by_id(expertise_id=expertise_id)
        if expertise is None or expertise.customer_id != user.id or user.role != UserRole.CUSTOMER:
            raise ExpertiseNotFoundError()

        if expertise.status != ExpertiseStatus.ACCEPTED or expertise.price is None:
            raise ExpertiseStateError("Акт доступен после приёмки работы с согласованной ценой")

        customer_company = await self.customers.get_company(expertise_id=expertise_id)
        payer = None
        if customer_company is not None:
            payer = ActPayer(
                name=customer_company.name,
                details=f"{customer_company.name}, ИНН {customer_company.inn}, КПП {customer_company.kpp or '—'}",
                address=customer_company.address,
            )

        if payer is None:
            individual = await self.customers.get_individual(expertise_id=expertise_id)
            if individual is not None:
                payer = ActPayer(
                    name=individual.full_name,
                    details=f"{individual.full_name}, паспорт {individual.passport_number}",
                    address=individual.address,
                )

        if payer is None:
            raise ExpertiseStateError("В заявке нет реквизитов заказчика")

        contract = await self.contracts.get_for_expertise(expertise_id=expertise_id)
        company = get_executor_requisites(
            kind=contract.kind if contract is not None else None,
            settings=self.settings,
        )
        subject = "Экспертиза промышленной безопасности"
        if expertise.object_name:
            subject += f": {expertise.object_name}"
        signed_at = expertise.accepted_at or expertise.created_at
        number = f"БЭ-{signed_at.year}-{expertise.id:04d}"
        act = ActData(
            number=number,
            amount=expertise.price,
            signed_at=signed_at,
            subject=subject,
            payer=payer,
        )
        content = await asyncio.to_thread(
            build_act_pdf,
            act=act,
            company=company,
            font_path=self.settings.pdf_font_path,
        )
        return GeneratedDocument(
            content=content,
            filename=f"Акт {number}.pdf",
            content_type="application/pdf",
        )
