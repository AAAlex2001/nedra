"""Зависимости подачи обращения."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.core.email_sender import EmailSender
from src.core.settings import Settings, get_settings
from src.requests.repositories.contact_requests import ContactRequestRepository
from src.requests.site.contact_request_letters import ContactRequestLetters
from src.requests.site.usecases.create_contact_request import CreateContactRequestUseCase


def get_create_contact_request_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> CreateContactRequestUseCase:
    """Подача обращения."""

    return CreateContactRequestUseCase(
        session=session,
        requests=ContactRequestRepository(session=session),
        letters=ContactRequestLetters(
            sender=EmailSender(settings=settings),
            recipients=settings.notify_emails,
        ),
    )
