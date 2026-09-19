"""Экспертиза: репозитории, фабрика сценария подачи, доступ к экспертизе из пути."""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.dependencies.experts import get_private_storage, get_profile_repository
from app.dependencies.users import get_current_user
from app.models.expertise import Expertise
from app.models.user import User, UserRole
from app.services.experts.repo import ExpertProfileRepository
from app.services.expertise.access import can_view
from app.services.expertise.repo import ExpertiseRepository
from app.services.expertise.usecases.create_expertise import CreateExpertiseUseCase
from app.services.files.storage import PrivateStorage
from app.services.notifications.repo import NotificationRepository


def get_expertise_repository(
    session: AsyncSession = Depends(get_session),
) -> ExpertiseRepository:
    """Репозиторий экспертиз с сессией текущего запроса."""

    return ExpertiseRepository(session)


def get_notification_repository(
    session: AsyncSession = Depends(get_session),
) -> NotificationRepository:
    """Репозиторий уведомлений с сессией текущего запроса."""

    return NotificationRepository(session)


def get_create_expertise_usecase(
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    profiles: ExpertProfileRepository = Depends(get_profile_repository),
    notifications: NotificationRepository = Depends(get_notification_repository),
    storage: PrivateStorage = Depends(get_private_storage),
) -> CreateExpertiseUseCase:
    """Сценарий подачи документации на экспертизу."""

    return CreateExpertiseUseCase(expertises, profiles, notifications, storage)


async def get_visible_expertise(
    expertise_id: int,
    user: User = Depends(get_current_user),
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    profiles: ExpertProfileRepository = Depends(get_profile_repository),
) -> Expertise:
    """Экспертиза из пути, доступная текущему пользователю. Чужая выглядит как несуществующая."""

    expertise = await expertises.get_by_id(expertise_id)

    certificates = []
    if user.role == UserRole.EXPERT:
        certificates = await profiles.list_certificates(user.id)

    if expertise is None or not can_view(expertise, user, certificates):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Экспертиза не найдена",
        )

    return expertise
