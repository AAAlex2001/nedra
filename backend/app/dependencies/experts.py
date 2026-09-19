"""Эксперты: репозитории, закрытое хранилище и фабрики сценариев."""

from pathlib import Path

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_session
from app.dependencies.users import get_user_repository
from app.services.experts.repo import ExpertApplicationRepository, ExpertProfileRepository
from app.services.experts.usecases.approve_application import ApproveExpertApplicationUseCase
from app.services.experts.usecases.delete_expert import DeleteExpertUseCase
from app.services.experts.usecases.reject_application import RejectExpertApplicationUseCase
from app.services.experts.usecases.submit_application import SubmitExpertApplicationUseCase
from app.services.files.storage import PrivateStorage
from app.services.users.repo import UserRepository


def get_application_repository(
    session: AsyncSession = Depends(get_session),
) -> ExpertApplicationRepository:
    """Репозиторий заявок экспертов с сессией текущего запроса."""

    return ExpertApplicationRepository(session)


def get_profile_repository(
    session: AsyncSession = Depends(get_session),
) -> ExpertProfileRepository:
    """Репозиторий профилей экспертов с сессией текущего запроса."""

    return ExpertProfileRepository(session)


def get_private_storage() -> PrivateStorage:
    """Закрытое хранилище файлов из каталога PRIVATE_DIR."""

    return PrivateStorage(Path(get_settings().private_dir))


def get_submit_application_usecase(
    applications: ExpertApplicationRepository = Depends(get_application_repository),
    users: UserRepository = Depends(get_user_repository),
    storage: PrivateStorage = Depends(get_private_storage),
) -> SubmitExpertApplicationUseCase:
    """Сценарий подачи заявки."""

    return SubmitExpertApplicationUseCase(applications, users, storage)


def get_approve_application_usecase(
    applications: ExpertApplicationRepository = Depends(get_application_repository),
    users: UserRepository = Depends(get_user_repository),
) -> ApproveExpertApplicationUseCase:
    """Сценарий одобрения заявки."""

    return ApproveExpertApplicationUseCase(applications, users)


def get_delete_expert_usecase(
    users: UserRepository = Depends(get_user_repository),
    applications: ExpertApplicationRepository = Depends(get_application_repository),
) -> DeleteExpertUseCase:
    """Сценарий удаления эксперта."""

    return DeleteExpertUseCase(users, applications)


def get_reject_application_usecase(
    applications: ExpertApplicationRepository = Depends(get_application_repository),
) -> RejectExpertApplicationUseCase:
    """Сценарий отклонения заявки."""

    return RejectExpertApplicationUseCase(applications)
