"""Административные сценарии работы."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.admin.usecases.delete_audit import DeleteAuditUseCase
from src.audit.admin.usecases.list_audits import ListAdminAuditsUseCase
from src.audit.admin.usecases.update_audit import UpdateAuditUseCase
from src.audit.audit_letters import AuditLetters
from src.audit.repositories.audit_applications import AuditApplicationRepository
from src.audit.repositories.audit_documents import AuditDocumentRepository
from src.audit.repositories.audit_payments import AuditPaymentRepository
from src.audit.repositories.audits import AuditRepository
from src.billing.repositories.invoices import InvoiceRepository
from src.core.database import get_session
from src.core.email_sender import EmailSender
from src.core.file_storage import FileStorage
from src.core.settings import Settings, get_settings
from src.notifications.repositories.notifications import NotificationRepository
from src.users.repositories.expert_profiles import ExpertProfileRepository
from src.users.repositories.users import UserRepository


def get_list_audits_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> ListAdminAuditsUseCase:
    """Просмотр списка работ."""

    return ListAdminAuditsUseCase(
        audits=AuditRepository(session=session),
        users=UserRepository(session=session),
        applications=AuditApplicationRepository(session=session),
    )


def get_update_audit_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> UpdateAuditUseCase:
    """Изменение работы."""

    return UpdateAuditUseCase(
        session=session,
        audits=AuditRepository(session=session),
        users=UserRepository(session=session),
        applications=AuditApplicationRepository(session=session),
        profiles=ExpertProfileRepository(session=session),
        notifications=NotificationRepository(session=session),
        letters=AuditLetters(
            sender=EmailSender(settings=settings),
            cabinet_url=settings.cabinet_url,
            manager_emails=settings.notify_emails,
        ),
    )


def get_delete_audit_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> DeleteAuditUseCase:
    """Удаление работы без платёжной истории."""

    return DeleteAuditUseCase(
        session=session,
        audits=AuditRepository(session=session),
        documents=AuditDocumentRepository(session=session),
        payments=AuditPaymentRepository(session=session),
        invoices=InvoiceRepository(session=session),
        storage=FileStorage(directory=settings.private_dir),
    )
