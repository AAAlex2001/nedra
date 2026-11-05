"""Зависимости профиля пользователя."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repositories.expert_applications import ExpertApplicationRepository
from src.core.database import get_session
from src.core.email_sender import EmailSender
from src.core.settings import Settings, get_settings
from src.users.repositories.email_changes import EmailChangeRepository
from src.users.repositories.users import UserRepository
from src.users.site.usecases.confirm_email_change import ConfirmEmailChangeUseCase
from src.users.site.usecases.request_email_change import RequestEmailChangeUseCase
from src.users.site.usecases.update_profile import UpdateProfileUseCase
from src.users.site.user_letters import UserLetters


def get_update_profile_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> UpdateProfileUseCase:
    """Изменение профиля."""

    return UpdateProfileUseCase(
        session=session,
        users=UserRepository(session=session),
        applications=ExpertApplicationRepository(session=session),
    )


def get_request_email_change_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> RequestEmailChangeUseCase:
    """Запрос кода на новый адрес."""

    return RequestEmailChangeUseCase(
        session=session,
        users=UserRepository(session=session),
        changes=EmailChangeRepository(session=session),
        letters=UserLetters(sender=EmailSender(settings=settings)),
    )


def get_confirm_email_change_usecase(
    *,
    session: AsyncSession = Depends(get_session),
) -> ConfirmEmailChangeUseCase:
    """Подтверждение новой почты."""

    return ConfirmEmailChangeUseCase(
        session=session,
        users=UserRepository(session=session),
        changes=EmailChangeRepository(session=session),
        applications=ExpertApplicationRepository(session=session),
    )
