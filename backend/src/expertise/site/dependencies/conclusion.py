"""Подготовка, передача и приёмка заключения."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.core.email_sender import EmailSender
from src.core.file_storage import FileStorage
from src.core.settings import Settings, get_settings
from src.expertise.repositories.expertise_documents import ExpertiseDocumentRepository
from src.expertise.repositories.expertises import ExpertiseRepository
from src.expertise.site.expertise_file_storage import ExpertiseFileStorage
from src.expertise.site.usecases.accept_work import AcceptExpertiseWorkUseCase
from src.expertise.site.usecases.mark_conclusion_ready import (
    MarkExpertiseConclusionReadyUseCase,
)
from src.expertise.site.usecases.send_conclusion import SendExpertiseConclusionUseCase
from src.notifications.email_delivery import NotificationEmailDelivery
from src.notifications.repositories.notifications import NotificationRepository
from src.users.repositories.users import UserRepository


def get_mark_conclusion_ready_expertise_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> MarkExpertiseConclusionReadyUseCase:
    """Сообщить о готовности заключения."""

    return MarkExpertiseConclusionReadyUseCase(
        session=session,
        expertises=ExpertiseRepository(session=session),
        notifications=NotificationRepository(session=session),
        email_delivery=NotificationEmailDelivery(
            users=UserRepository(session=session),
            sender=EmailSender(settings=settings),
            cabinet_url=settings.cabinet_url,
        ),
    )


def get_accept_work_expertise_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> AcceptExpertiseWorkUseCase:
    """Принять выполненную работу."""

    return AcceptExpertiseWorkUseCase(
        session=session,
        expertises=ExpertiseRepository(session=session),
        notifications=NotificationRepository(session=session),
        email_delivery=NotificationEmailDelivery(
            users=UserRepository(session=session),
            sender=EmailSender(settings=settings),
            cabinet_url=settings.cabinet_url,
        ),
    )


def get_send_conclusion_expertise_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> SendExpertiseConclusionUseCase:
    """Передать заключение заказчику."""

    return SendExpertiseConclusionUseCase(
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
    )
