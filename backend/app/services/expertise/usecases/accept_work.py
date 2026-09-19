"""Шаг 12: заказчик скачал заключение и принял работу."""

from datetime import datetime, timezone

from app.models.expertise import Expertise, ExpertiseStatus
from app.models.notification import Notification
from app.models.user import User
from app.services.expertise.exceptions import ExpertiseAccessError, ExpertiseStateError
from app.services.expertise.repo import ExpertiseRepository
from app.services.notifications.repo import NotificationRepository


class AcceptWorkUseCase:
    """Закрыть экспертизу статусом accepted и сообщить эксперту."""

    def __init__(
        self, expertises: ExpertiseRepository, notifications: NotificationRepository
    ) -> None:
        self.expertises = expertises
        self.notifications = notifications

    async def execute(self, customer: User, expertise: Expertise) -> Expertise:
        """Бросает ExpertiseStateError и ExpertiseAccessError."""

        if expertise.customer_id != customer.id:
            raise ExpertiseAccessError("Принять работу может только заказчик этой заявки")

        if expertise.status != ExpertiseStatus.SENT or expertise.expert_id is None:
            raise ExpertiseStateError("Заключение ещё не отправлено")

        expertise.accepted_at = datetime.now(timezone.utc)
        expertise.status = ExpertiseStatus.ACCEPTED

        self.notifications.add_all(
            [
                Notification(
                    user_id=expertise.expert_id,
                    expertise_id=expertise.id,
                    text=f"Заказчик принял работу по заявке №{expertise.id}",
                )
            ]
        )

        return await self.expertises.save(expertise)
