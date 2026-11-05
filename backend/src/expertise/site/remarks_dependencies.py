"""Замечания и исправленные документы."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.core.email_sender import EmailSender
from src.core.file_storage import FileStorage
from src.core.settings import Settings, get_settings
from src.expertise.repositories.expertise_documents import ExpertiseDocumentRepository
from src.expertise.repositories.expertise_remarks import ExpertiseRemarkRepository
from src.expertise.repositories.expertises import ExpertiseRepository
from src.expertise.site.expertise_file_storage import ExpertiseFileStorage
from src.expertise.site.usecases.resubmit_documents import ResubmitExpertiseDocumentsUseCase
from src.expertise.site.usecases.send_remarks import SendExpertiseRemarksUseCase
from src.notifications.email_delivery import NotificationEmailDelivery
from src.notifications.repositories.notifications import NotificationRepository
from src.users.repositories.users import UserRepository


def get_send_remarks_expertise_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> SendExpertiseRemarksUseCase:
    """Отправить замечания заказчику."""

    return SendExpertiseRemarksUseCase(
        session=session,
        expertises=ExpertiseRepository(session=session),
        notifications=NotificationRepository(session=session),
        email_delivery=NotificationEmailDelivery(
            users=UserRepository(session=session),
            sender=EmailSender(settings=settings),
            cabinet_url=settings.cabinet_url,
        ),
        documents=ExpertiseDocumentRepository(session=session),
        file_storage=ExpertiseFileStorage(
            storage=FileStorage(directory=settings.private_dir),
        ),
        remarks=ExpertiseRemarkRepository(session=session),
    )


def get_resubmit_documents_expertise_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> ResubmitExpertiseDocumentsUseCase:
    """Отправить исправленные документы."""

    return ResubmitExpertiseDocumentsUseCase(
        session=session,
        expertises=ExpertiseRepository(session=session),
        notifications=NotificationRepository(session=session),
        email_delivery=NotificationEmailDelivery(
            users=UserRepository(session=session),
            sender=EmailSender(settings=settings),
            cabinet_url=settings.cabinet_url,
        ),
        documents=ExpertiseDocumentRepository(session=session),
        file_storage=ExpertiseFileStorage(
            storage=FileStorage(directory=settings.private_dir),
        ),
        remarks=ExpertiseRemarkRepository(session=session),
    )
