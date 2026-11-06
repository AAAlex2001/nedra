"""Счета и оплата."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.repositories.audit_applications import AuditApplicationRepository
from src.audit.repositories.audit_customers import AuditCustomerRepository
from src.audit.repositories.audit_payments import AuditPaymentRepository
from src.audit.repositories.audits import AuditRepository
from src.audit.site.dependencies.access import get_audit_access
from src.audit.site.usecases.get_act import GetAuditActUseCase
from src.audit.site.usecases.get_audit_payments import GetAuditPaymentsUseCase
from src.audit.site.usecases.issue_invoice import IssueAuditInvoiceUseCase
from src.billing.repositories.invoices import InvoiceRepository
from src.contracts.repositories.contracts import ContractRepository
from src.core.database import get_session
from src.core.settings import Settings, get_settings
from src.payments.repositories.payments import PaymentRepository


def get_audit_payments_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> GetAuditPaymentsUseCase:
    """Оплата аудита."""

    return GetAuditPaymentsUseCase(
        access=get_audit_access(session=session),
        stages=AuditPaymentRepository(session=session),
        payments=PaymentRepository(session=session),
        invoices=InvoiceRepository(session=session),
    )


def get_issue_invoice_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> IssueAuditInvoiceUseCase:
    """Выставление счёта заказчику."""

    return IssueAuditInvoiceUseCase(
        session=session,
        audits=AuditRepository(session=session),
        customers=AuditCustomerRepository(session=session),
        invoices=InvoiceRepository(session=session),
    )


def get_act_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> GetAuditActUseCase:
    """Скачивание акта выполненных работ."""

    return GetAuditActUseCase(
        audits=AuditRepository(session=session),
        customers=AuditCustomerRepository(session=session),
        contracts=ContractRepository(session=session),
        settings=settings,
        applications=AuditApplicationRepository(session=session),
    )
