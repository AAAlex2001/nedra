"""Замечания и исправленные документы."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.repositories.audit_documents import AuditDocumentRepository
from src.audit.repositories.audit_remarks import AuditRemarkRepository
from src.audit.repositories.audits import AuditRepository
from src.audit.site.audit_file_storage import AuditFileStorage
from src.audit.site.usecases.resubmit_documents import ResubmitAuditDocumentsUseCase
from src.audit.site.usecases.send_remarks import SendAuditRemarksUseCase
from src.core.database import get_session
from src.core.email_sender import EmailSender
from src.core.file_storage import FileStorage
from src.core.settings import Settings, get_settings
from src.notifications.email_delivery import NotificationEmailDelivery
from src.notifications.repositories.notifications import NotificationRepository
from src.users.repositories.users import UserRepository


def get_send_remarks_audit_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> SendAuditRemarksUseCase:
    """Отправить замечания заказчику."""

    return SendAuditRemarksUseCase(
        session=session,
        audits=AuditRepository(session=session),
        notifications=NotificationRepository(session=session),
        email_delivery=NotificationEmailDelivery(
            users=UserRepository(session=session),
            sender=EmailSender(settings=settings),
            cabinet_url=settings.cabinet_url,
        ),
        documents=AuditDocumentRepository(session=session),
        file_storage=AuditFileStorage(
            storage=FileStorage(directory=settings.private_dir),
        ),
        remarks=AuditRemarkRepository(session=session),
    )


def get_resubmit_documents_audit_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> ResubmitAuditDocumentsUseCase:
    """Отправить исправленные документы."""

    return ResubmitAuditDocumentsUseCase(
        session=session,
        audits=AuditRepository(session=session),
        notifications=NotificationRepository(session=session),
        email_delivery=NotificationEmailDelivery(
            users=UserRepository(session=session),
            sender=EmailSender(settings=settings),
            cabinet_url=settings.cabinet_url,
        ),
        documents=AuditDocumentRepository(session=session),
        file_storage=AuditFileStorage(
            storage=FileStorage(directory=settings.private_dir),
        ),
        remarks=AuditRemarkRepository(session=session),
    )
