"""Зависимости регистрации экспертов."""

from fastapi import Depends, Form
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repositories.expert_applications import ExpertApplicationRepository
from src.auth.site.expert_application_letters import ExpertApplicationLetters
from src.auth.site.schemas.expert_application import CreateExpertApplicationRequest
from src.auth.site.usecases.submit_expert_application import (
    SubmitExpertApplicationUseCase,
)
from src.core.database import get_session
from src.core.email_sender import EmailSender
from src.core.settings import Settings, get_settings
from src.users.repositories.users import UserRepository


def parse_expert_application_form(*, payload: str = Form()) -> CreateExpertApplicationRequest:
    """Прочитать заявку из формы."""

    try:
        return CreateExpertApplicationRequest.model_validate_json(payload)
    except ValidationError as error:
        raise RequestValidationError(
            error.errors(
                include_input=False,
                include_context=False,
            )
        ) from error


def get_expert_application_letters(*, settings: Settings) -> ExpertApplicationLetters:
    """Письма заявителю и менеджерам."""

    return ExpertApplicationLetters(
        sender=EmailSender(settings=settings),
        manager_emails=settings.notify_emails,
    )


def get_submit_expert_application_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> SubmitExpertApplicationUseCase:
    """Подача заявки эксперта."""

    return SubmitExpertApplicationUseCase(
        session=session,
        applications=ExpertApplicationRepository(session=session),
        users=UserRepository(session=session),
        letters=get_expert_application_letters(settings=settings),
    )
