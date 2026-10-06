"""Шаг 8: эксперт закончил работу и сообщает, что заключение готово."""

from datetime import datetime, timezone

from app.models.expertise import Expertise, ExpertiseStatus
from app.models.notification import Notification
from app.models.user import User
from app.services.expertise.exceptions import ExpertiseAccessError, ExpertiseStateError
from app.services.expertise.repo import ExpertiseRepository
from app.services.expertise.wording import wording_for
from app.services.notifications.repo import NotificationRepository


class MarkConclusionReadyUseCase:
    """Перевести экспертизу в conclusion_ready и попросить заказчика оплатить остаток."""

    def __init__(
        self, expertises: ExpertiseRepository, notifications: NotificationRepository
    ) -> None:
        self.expertises = expertises
        self.notifications = notifications

    async def execute(self, expert: User, expertise: Expertise) -> Expertise:
        """Бросает ExpertiseStateError и ExpertiseAccessError."""

        if expertise.expert_id != expert.id:
            raise ExpertiseAccessError("Это не ваша экспертиза")

        if expertise.status != ExpertiseStatus.IN_PROGRESS:
            raise ExpertiseStateError("Сначала должен быть оплачен аванс")

        expertise.conclusion_ready_at = datetime.now(timezone.utc)
        expertise.status = ExpertiseStatus.CONCLUSION_READY

        words = wording_for(expertise)
        self.notifications.add_all(
            [
                Notification(
                    user_id=expertise.customer_id,
                    expertise_id=expertise.id,
                    text=f"{words.result} по заявке №{expertise.id} {words.result_ready}. Оплатите остаток, чтобы получить его",
                )
            ]
        )

        return await self.expertises.save(expertise)
