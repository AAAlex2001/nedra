"""Экспертиза: репозитории, фабрики сценариев по шагам, доступ к экспертизе из пути."""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.dependencies.experts import get_private_storage, get_profile_repository
from app.dependencies.payments import get_create_payment_usecase, get_payment_repository
from app.dependencies.tariffs import get_tariff_repository
from app.dependencies.users import get_current_user
from app.models.expertise import Expertise
from app.models.user import User, UserRole
from app.services.experts.repo import ExpertProfileRepository
from app.services.expertise.access import can_view
from app.services.expertise.repo import ExpertiseRepository
from app.services.expertise.usecases.accept_expertise import AcceptExpertiseUseCase
from app.services.expertise.usecases.accept_work import AcceptWorkUseCase
from app.services.expertise.usecases.apply_expertise_payment import ApplyExpertisePaymentUseCase
from app.services.expertise.usecases.confirm_expertise import ConfirmExpertiseUseCase
from app.services.expertise.usecases.create_expertise import CreateExpertiseUseCase
from app.services.expertise.usecases.create_expertise_payment import CreateExpertisePaymentUseCase
from app.services.expertise.usecases.manage_expertise import (
    DeleteExpertiseUseCase,
    UpdateExpertiseUseCase,
)
from app.services.expertise.usecases.mark_conclusion_ready import MarkConclusionReadyUseCase
from app.services.expertise.usecases.resubmit_documentation import ResubmitDocumentationUseCase
from app.services.expertise.usecases.send_conclusion import SendConclusionUseCase
from app.services.expertise.usecases.send_remarks import SendRemarksUseCase
from app.services.files.storage import PrivateStorage
from app.services.notifications.repo import NotificationRepository
from app.services.payments.repo import PaymentRepository
from app.services.payments.usecases.create_payment import CreatePaymentUseCase
from app.services.tariffs.repo import TariffRepository


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
    tariffs: TariffRepository = Depends(get_tariff_repository),
    storage: PrivateStorage = Depends(get_private_storage),
) -> CreateExpertiseUseCase:
    """Сценарий подачи документации на экспертизу."""

    return CreateExpertiseUseCase(expertises, profiles, notifications, tariffs, storage)


def get_accept_expertise_usecase(
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    profiles: ExpertProfileRepository = Depends(get_profile_repository),
    notifications: NotificationRepository = Depends(get_notification_repository),
) -> AcceptExpertiseUseCase:
    """Сценарий «эксперт готов провести экспертизу»."""

    return AcceptExpertiseUseCase(expertises, profiles, notifications)


def get_confirm_expertise_usecase(
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    notifications: NotificationRepository = Depends(get_notification_repository),
    storage: PrivateStorage = Depends(get_private_storage),
) -> ConfirmExpertiseUseCase:
    """Сценарий «заказчик подписал договор»."""

    return ConfirmExpertiseUseCase(expertises, notifications, storage)


def get_create_expertise_payment_usecase(
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    payments: PaymentRepository = Depends(get_payment_repository),
    create_payment: CreatePaymentUseCase = Depends(get_create_payment_usecase),
) -> CreateExpertisePaymentUseCase:
    """Сценарий создания платежа за этап экспертизы."""

    return CreateExpertisePaymentUseCase(expertises, payments, create_payment)


def get_apply_expertise_payment_usecase(
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    notifications: NotificationRepository = Depends(get_notification_repository),
) -> ApplyExpertisePaymentUseCase:
    """Сценарий продвижения экспертизы по оплаченному платежу."""

    return ApplyExpertisePaymentUseCase(expertises, notifications)


def get_mark_conclusion_ready_usecase(
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    notifications: NotificationRepository = Depends(get_notification_repository),
) -> MarkConclusionReadyUseCase:
    """Сценарий «заключение готово»."""

    return MarkConclusionReadyUseCase(expertises, notifications)


def get_send_remarks_usecase(
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    notifications: NotificationRepository = Depends(get_notification_repository),
    storage: PrivateStorage = Depends(get_private_storage),
) -> SendRemarksUseCase:
    """Сценарий выдачи замечаний по документации."""

    return SendRemarksUseCase(expertises, notifications, storage)


def get_resubmit_documentation_usecase(
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    notifications: NotificationRepository = Depends(get_notification_repository),
    storage: PrivateStorage = Depends(get_private_storage),
) -> ResubmitDocumentationUseCase:
    """Сценарий повторной подачи исправленной документации."""

    return ResubmitDocumentationUseCase(expertises, notifications, storage)


def get_send_conclusion_usecase(
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    notifications: NotificationRepository = Depends(get_notification_repository),
    storage: PrivateStorage = Depends(get_private_storage),
) -> SendConclusionUseCase:
    """Сценарий отправки подписанного заключения."""

    return SendConclusionUseCase(expertises, notifications, storage)


def get_accept_work_usecase(
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    notifications: NotificationRepository = Depends(get_notification_repository),
) -> AcceptWorkUseCase:
    """Сценарий «работа принята»."""

    return AcceptWorkUseCase(expertises, notifications)


def get_update_expertise_usecase(
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
) -> UpdateExpertiseUseCase:
    """Сценарий правки заявки администратором."""

    return UpdateExpertiseUseCase(expertises)


def get_delete_expertise_usecase(
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    storage: PrivateStorage = Depends(get_private_storage),
) -> DeleteExpertiseUseCase:
    """Сценарий удаления заявки вместе с файлами."""

    return DeleteExpertiseUseCase(expertises, storage)


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
