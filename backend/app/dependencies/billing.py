"""Биллинг: репозитории реквизитов и счетов, фабрики сценариев."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.dependencies.experts import get_private_storage
from app.dependencies.expertise import get_expertise_repository, get_notification_repository
from app.services.billing.repo import CustomerCompanyRepository, InvoiceRepository
from app.services.billing.usecases.confirm_invoice import ConfirmInvoiceUseCase
from app.services.billing.usecases.issue_invoice import IssueInvoiceUseCase
from app.services.billing.usecases.report_payment import ReportInvoicePaidUseCase
from app.services.billing.usecases.save_company import SaveCustomerCompanyUseCase
from app.services.expertise.repo import ExpertiseRepository
from app.services.files.storage import PrivateStorage
from app.services.notifications.repo import NotificationRepository


def get_company_repository(
    session: AsyncSession = Depends(get_session),
) -> CustomerCompanyRepository:
    """Репозиторий реквизитов заказчиков с сессией текущего запроса."""

    return CustomerCompanyRepository(session)


def get_invoice_repository(
    session: AsyncSession = Depends(get_session),
) -> InvoiceRepository:
    """Репозиторий счетов с сессией текущего запроса."""

    return InvoiceRepository(session)


def get_save_company_usecase(
    companies: CustomerCompanyRepository = Depends(get_company_repository),
) -> SaveCustomerCompanyUseCase:
    """Сценарий сохранения реквизитов организации."""

    return SaveCustomerCompanyUseCase(companies)


def get_issue_invoice_usecase(
    invoices: InvoiceRepository = Depends(get_invoice_repository),
    companies: CustomerCompanyRepository = Depends(get_company_repository),
) -> IssueInvoiceUseCase:
    """Сценарий выставления счёта."""

    return IssueInvoiceUseCase(invoices, companies)


def get_report_payment_usecase(
    invoices: InvoiceRepository = Depends(get_invoice_repository),
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    storage: PrivateStorage = Depends(get_private_storage),
    notifications: NotificationRepository = Depends(get_notification_repository),
) -> ReportInvoicePaidUseCase:
    """Сценарий «заказчик сообщил об оплате счёта»."""

    return ReportInvoicePaidUseCase(invoices, expertises, storage, notifications)


def get_confirm_invoice_usecase(
    invoices: InvoiceRepository = Depends(get_invoice_repository),
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    notifications: NotificationRepository = Depends(get_notification_repository),
) -> ConfirmInvoiceUseCase:
    """Сценарий подтверждения оплаты по счёту."""

    return ConfirmInvoiceUseCase(invoices, expertises, notifications)
