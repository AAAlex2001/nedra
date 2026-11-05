"""Сообщить о готовности заключения."""

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.expertise.enums import ExpertiseStatus
from src.expertise.exceptions import ExpertiseNotFoundError, ExpertiseStateError
from src.expertise.repositories.expertises import ExpertiseRepository
from src.expertise.schemas.expertise import ExpertiseResponse
from src.notifications.email_delivery import NotificationEmailDelivery
from src.notifications.models.notification import Notification
from src.notifications.repositories.notifications import NotificationRepository
from src.users.enums import UserRole
from src.users.models.user import User


class MarkExpertiseConclusionReadyUseCase:
    """Сообщить о готовности заключения."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        expertises: ExpertiseRepository,
        notifications: NotificationRepository,
        email_delivery: NotificationEmailDelivery,
    ) -> None:
        """Хранение и уведомления."""

        self.session = session
        self.expertises = expertises
        self.notifications = notifications
        self.email_delivery = email_delivery

    async def execute(
        self,
        *,
        expertise_id: int,
        user: User,
    ) -> ExpertiseResponse:
        """Сообщить о готовности заключения."""

        expertise = await self.expertises.get_for_update(expertise_id=expertise_id)

        if expertise is None or expertise.expert_id != user.id or user.role != UserRole.EXPERT:
            raise ExpertiseNotFoundError()

        if expertise.status != ExpertiseStatus.IN_PROGRESS:
            raise ExpertiseStateError("Действие недоступно на этом этапе")

        notification = Notification(
            user_id=expertise.customer_id,
            expertise_id=expertise_id,
            text=f"Заключение готово к выдаче, №{expertise_id}",
        )

        expertise.status = ExpertiseStatus.CONCLUSION_READY
        expertise.conclusion_ready_at = datetime.now(UTC)
        await self.expertises.save(expertise=expertise)
        await self.notifications.add(notification=notification)
        response = ExpertiseResponse.from_model(expertise=expertise)

        await self.session.commit()
        await self.email_delivery.send(notification=notification)

        return response
