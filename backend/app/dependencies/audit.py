"""Аудит СУПБ: фабрика сценария подачи заявки."""

from fastapi import Depends

from app.dependencies.experts import get_private_storage, get_profile_repository
from app.dependencies.expertise import get_expertise_repository, get_notification_repository
from app.services.audit.usecases.create_audit import CreateAuditUseCase
from app.services.experts.repo import ExpertProfileRepository
from app.services.expertise.repo import ExpertiseRepository
from app.services.files.storage import PrivateStorage
from app.services.notifications.repo import NotificationRepository


def get_create_audit_usecase(
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    profiles: ExpertProfileRepository = Depends(get_profile_repository),
    notifications: NotificationRepository = Depends(get_notification_repository),
    storage: PrivateStorage = Depends(get_private_storage),
) -> CreateAuditUseCase:
    """Сценарий подачи заявки на аудит СУПБ."""

    return CreateAuditUseCase(expertises, profiles, notifications, storage)
