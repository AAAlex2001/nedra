"""Зависимости счетов заказчика."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.repositories.audit_applications import AuditApplicationRepository
from src.audit.repositories.audit_documents import AuditDocumentRepository
from src.audit.repositories.audits import AuditRepository
from src.billing.invoice_attachments import InvoiceAttachments
from src.billing.invoice_letters import InvoiceLetters
from src.billing.repositories.invoices import InvoiceRepository
from src.billing.site.usecases.get_invoice_document import GetInvoiceDocumentUseCase
from src.billing.site.usecases.list_acts import ListActsUseCase
from src.billing.site.usecases.list_invoices import ListInvoicesUseCase
from src.billing.site.usecases.report_invoice_payment import ReportInvoicePaymentUseCase
from src.contracts.repositories.contracts import ContractRepository
from src.core.database import get_session
from src.core.email_sender import EmailSender
from src.core.file_storage import FileStorage
from src.core.settings import Settings, get_settings
from src.expertise.repositories.expertise_documents import ExpertiseDocumentRepository
from src.expertise.repositories.expertises import ExpertiseRepository
from src.notifications.repositories.notifications import NotificationRepository


def get_list_invoices_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> ListInvoicesUseCase:
    """Просмотр своих счетов."""

    return ListInvoicesUseCase(invoices=InvoiceRepository(session=session))


def get_report_invoice_payment_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> ReportInvoicePaymentUseCase:
    """Сообщение об оплате счёта."""

    return ReportInvoicePaymentUseCase(
        session=session,
        invoices=InvoiceRepository(session=session),
        attachments=InvoiceAttachments(
            storage=FileStorage(directory=settings.private_dir),
            audit_documents=AuditDocumentRepository(session=session),
            expertise_documents=ExpertiseDocumentRepository(session=session),
        ),
        notifications=NotificationRepository(session=session),
        letters=InvoiceLetters(
            sender=EmailSender(settings=settings),
            recipients=settings.notify_emails,
        ),
    )


def get_invoice_document_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> GetInvoiceDocumentUseCase:
    """Скачивание счёта в PDF."""

    return GetInvoiceDocumentUseCase(
        invoices=InvoiceRepository(session=session),
        contracts=ContractRepository(session=session),
        applications=AuditApplicationRepository(session=session),
        expertises=ExpertiseRepository(session=session),
        settings=settings,
    )


def get_list_acts_usecase(*, session: AsyncSession = Depends(get_session)) -> ListActsUseCase:
    """Просмотр актов заказчика."""

    return ListActsUseCase(
        audits=AuditRepository(session=session),
        applications=AuditApplicationRepository(session=session),
        expertises=ExpertiseRepository(session=session),
    )
