"""Шаг 5–6: заказчик готов оплатить, договор считается заключённым."""

from datetime import datetime, timezone

from app.models.expertise import Expertise, ExpertiseStatus
from app.models.notification import Notification
from app.models.user import User
from app.services.expertise.exceptions import ExpertiseAccessError, ExpertiseStateError
from app.services.expertise.repo import ExpertiseRepository
from app.services.notifications.repo import NotificationRepository


class ConfirmExpertiseUseCase:
    """Вторая галочка: обе стороны согласны, договор заключён, можно платить аванс."""

    def __init__(
        self, expertises: ExpertiseRepository, notifications: NotificationRepository
    ) -> None:
        self.expertises = expertises
        self.notifications = notifications

    async def execute(self, customer: User, expertise: Expertise) -> Expertise:
        """Перевести заявку в contract. Бросает ExpertiseStateError и ExpertiseAccessError."""

        if expertise.customer_id != customer.id:
            raise ExpertiseAccessError("Подтвердить может только заказчик этой заявки")

        if expertise.status != ExpertiseStatus.EXPERT_READY or expertise.expert_id is None:
            raise ExpertiseStateError("Эксперт ещё не подтвердил готовность")

        expertise.contract_at = datetime.now(timezone.utc)
        expertise.status = ExpertiseStatus.CONTRACT

        self.notifications.add_all(
            [
                Notification(
                    user_id=expertise.expert_id,
                    expertise_id=expertise.id,
                    text=f"Заказчик подтвердил заявку №{expertise.id}: договор заключён, ждём аванс",
                )
            ]
        )

        return await self.expertises.save(expertise)
