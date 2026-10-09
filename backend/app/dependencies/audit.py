"""Аудит СУПБ: фабрики сценариев подачи, торга, группы и Плана аудита."""

from fastapi import Depends

from app.dependencies.experts import get_private_storage, get_profile_repository
from app.dependencies.expertise import get_expertise_repository, get_notification_repository
from app.services.audit.usecases.create_audit import CreateAuditUseCase
from app.services.audit.usecases.negotiate import (
    AnswerCounterUseCase,
    AnswerOfferUseCase,
    ProposePriceUseCase,
)
from app.services.audit.usecases.plan import (
    ApprovePlanUseCase,
    RequestPlanChangesUseCase,
    SendPlanUseCase,
)
from app.services.audit.usecases.team import SetAuditTeamUseCase
from app.services.audit.usecases.upload_documents import UploadAuditDocumentsUseCase
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


def get_propose_price_usecase(
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    profiles: ExpertProfileRepository = Depends(get_profile_repository),
    notifications: NotificationRepository = Depends(get_notification_repository),
) -> ProposePriceUseCase:
    """Сценарий «руководитель группы предлагает свою цену»."""

    return ProposePriceUseCase(expertises, profiles, notifications)


def get_answer_offer_usecase(
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    notifications: NotificationRepository = Depends(get_notification_repository),
) -> AnswerOfferUseCase:
    """Сценарий ответа заказчика на предложенную цену."""

    return AnswerOfferUseCase(expertises, notifications)


def get_answer_counter_usecase(
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    notifications: NotificationRepository = Depends(get_notification_repository),
) -> AnswerCounterUseCase:
    """Сценарий ответа руководителя группы на цену заказчика."""

    return AnswerCounterUseCase(expertises, notifications)


def get_set_team_usecase(
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    profiles: ExpertProfileRepository = Depends(get_profile_repository),
    notifications: NotificationRepository = Depends(get_notification_repository),
) -> SetAuditTeamUseCase:
    """Сценарий формирования аудиторской группы."""

    return SetAuditTeamUseCase(expertises, profiles, notifications)


def get_send_plan_usecase(
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    notifications: NotificationRepository = Depends(get_notification_repository),
    storage: PrivateStorage = Depends(get_private_storage),
) -> SendPlanUseCase:
    """Сценарий отправки Плана аудита заказчику."""

    return SendPlanUseCase(expertises, notifications, storage)


def get_approve_plan_usecase(
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    notifications: NotificationRepository = Depends(get_notification_repository),
) -> ApprovePlanUseCase:
    """Сценарий согласования Плана заказчиком."""

    return ApprovePlanUseCase(expertises, notifications)


def get_request_plan_changes_usecase(
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    notifications: NotificationRepository = Depends(get_notification_repository),
) -> RequestPlanChangesUseCase:
    """Сценарий запроса корректировок Плана."""

    return RequestPlanChangesUseCase(expertises, notifications)


def get_upload_audit_documents_usecase(
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    notifications: NotificationRepository = Depends(get_notification_repository),
    storage: PrivateStorage = Depends(get_private_storage),
) -> UploadAuditDocumentsUseCase:
    """Сценарий загрузки документов по перечню после согласования Плана."""

    return UploadAuditDocumentsUseCase(expertises, notifications, storage)
