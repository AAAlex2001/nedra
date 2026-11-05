"""Скачивание акта выполненных работ."""

import asyncio

from src.audit.enums import AuditStatus
from src.audit.exceptions import AuditNotFoundError, AuditStateError
from src.audit.repositories.audit_applications import AuditApplicationRepository
from src.audit.repositories.audit_customers import AuditCustomerRepository
from src.audit.repositories.audits import AuditRepository
from src.billing.act_data import ActData, ActPayer
from src.billing.documents.act_pdf import build_act_pdf
from src.contracts.executors import get_executor_requisites
from src.contracts.repositories.contracts import ContractRepository
from src.core.settings import Settings
from src.documents.generated_document import GeneratedDocument
from src.users.enums import UserRole
from src.users.models.user import User


class GetAuditActUseCase:
    """Акт по принятой заказчиком работе."""

    def __init__(
        self,
        *,
        audits: AuditRepository,
        customers: AuditCustomerRepository,
        contracts: ContractRepository,
        settings: Settings,
        applications: AuditApplicationRepository,
    ) -> None:
        """Работы, реквизиты и договоры."""

        self.audits = audits
        self.customers = customers
        self.contracts = contracts
        self.settings = settings
        self.applications = applications

    async def execute(
        self,
        *,
        audit_id: int,
        user: User,
    ) -> GeneratedDocument:
        """Создать акт выполненных работ."""

        audit = await self.audits.get_by_id(audit_id=audit_id)
        if audit is None or audit.customer_id != user.id or user.role != UserRole.CUSTOMER:
            raise AuditNotFoundError()

        if audit.status != AuditStatus.ACCEPTED or audit.agreed_price is None:
            raise AuditStateError("Акт доступен после приёмки работы с согласованной ценой")

        customer_company = await self.customers.get_company(audit_id=audit_id)
        payer = None
        if customer_company is not None:
            payer = ActPayer(
                name=customer_company.name,
                details=f"{customer_company.name}, ИНН {customer_company.inn}, КПП {customer_company.kpp or '—'}",
                address=customer_company.address,
            )

        if payer is None:
            raise AuditStateError("В заявке нет реквизитов заказчика")

        contract = await self.contracts.get_for_audit(audit_id=audit_id)
        company = get_executor_requisites(
            kind=contract.kind if contract is not None else None,
            settings=self.settings,
        )
        application = await self.applications.get(audit_id=audit_id)
        subject = "Аудит СУПБ"
        if application is not None and application.object_name:
            subject += f": {application.object_name}"
        signed_at = audit.accepted_at or audit.created_at
        number = f"БА-{signed_at.year}-{audit.id:04d}"
        act = ActData(
            number=number,
            amount=audit.agreed_price,
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
