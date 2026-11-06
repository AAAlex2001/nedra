"""Подготовка, передача и приёмка заключения."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.repositories.audit_documents import AuditDocumentRepository
from src.audit.repositories.audits import AuditRepository
from src.audit.site.audit_file_storage import AuditFileStorage
from src.audit.site.usecases.accept_work import AcceptAuditWorkUseCase
from src.audit.site.usecases.mark_conclusion_ready import (
    MarkAuditConclusionReadyUseCase,
)
from src.audit.site.usecases.send_conclusion import SendAuditConclusionUseCase
from src.core.database import get_session
from src.core.email_sender import EmailSender
from src.core.file_storage import FileStorage
from src.core.settings import Settings, get_settings
from src.notifications.email_delivery import NotificationEmailDelivery
from src.notifications.repositories.notifications import NotificationRepository
from src.users.repositories.users import UserRepository


def get_mark_conclusion_ready_audit_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> MarkAuditConclusionReadyUseCase:
    """Сообщить о готовности заключения."""

    return MarkAuditConclusionReadyUseCase(
        session=session,
        audits=AuditRepository(session=session),
        notifications=NotificationRepository(session=session),
        email_delivery=NotificationEmailDelivery(
            users=UserRepository(session=session),
            sender=EmailSender(settings=settings),
            cabinet_url=settings.cabinet_url,
        ),
    )


def get_accept_work_audit_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> AcceptAuditWorkUseCase:
    """Принять выполненную работу."""

    return AcceptAuditWorkUseCase(
        session=session,
        audits=AuditRepository(session=session),
        notifications=NotificationRepository(session=session),
        email_delivery=NotificationEmailDelivery(
            users=UserRepository(session=session),
            sender=EmailSender(settings=settings),
            cabinet_url=settings.cabinet_url,
        ),
    )


def get_send_conclusion_audit_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> SendAuditConclusionUseCase:
    """Передать заключение заказчику."""

    return SendAuditConclusionUseCase(
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
    )
