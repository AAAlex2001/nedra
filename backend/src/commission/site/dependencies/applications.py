"""Зависимости подачи заявки кандидата."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.commission.repositories.commission_applications import (
    CommissionApplicationRepository,
)
from src.commission.site.commission_letters import CommissionLetters
from src.commission.site.usecases.create_commission_application import (
    CreateCommissionApplicationUseCase,
)
from src.core.database import get_session
from src.core.email_sender import EmailSender
from src.core.settings import Settings, get_settings


def get_create_commission_application_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> CreateCommissionApplicationUseCase:
    """Подача заявки кандидата."""

    return CreateCommissionApplicationUseCase(
        session=session,
        applications=CommissionApplicationRepository(session=session),
        letters=CommissionLetters(
            sender=EmailSender(settings=settings),
            recipients=settings.notify_emails,
        ),
    )
