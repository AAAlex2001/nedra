"""Счета и оплата."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.billing.repositories.invoices import InvoiceRepository
from src.contracts.repositories.contracts import ContractRepository
from src.core.database import get_session
from src.core.settings import Settings, get_settings
from src.expertise.repositories.expertise_customers import ExpertiseCustomerRepository
from src.expertise.repositories.expertise_payments import ExpertisePaymentRepository
from src.expertise.repositories.expertises import ExpertiseRepository
from src.expertise.site.dependencies import get_expertise_access
from src.expertise.site.usecases.get_act import GetExpertiseActUseCase
from src.expertise.site.usecases.get_expertise_payments import GetExpertisePaymentsUseCase
from src.expertise.site.usecases.issue_invoice import IssueExpertiseInvoiceUseCase
from src.payments.repositories.payments import PaymentRepository


def get_expertise_payments_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> GetExpertisePaymentsUseCase:
    """Оплата экспертизы."""

    return GetExpertisePaymentsUseCase(
        access=get_expertise_access(session=session),
        stages=ExpertisePaymentRepository(session=session),
        payments=PaymentRepository(session=session),
        invoices=InvoiceRepository(session=session),
    )


def get_issue_invoice_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> IssueExpertiseInvoiceUseCase:
    """Выставление счёта заказчику."""

    return IssueExpertiseInvoiceUseCase(
        session=session,
        expertises=ExpertiseRepository(session=session),
        customers=ExpertiseCustomerRepository(session=session),
        invoices=InvoiceRepository(session=session),
    )


def get_act_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> GetExpertiseActUseCase:
    """Скачивание акта выполненных работ."""

    return GetExpertiseActUseCase(
        expertises=ExpertiseRepository(session=session),
        customers=ExpertiseCustomerRepository(session=session),
        contracts=ContractRepository(session=session),
        settings=settings,
    )
