"""Реакция экспертизы на оплаченный платёж: аванс запускает работу, остаток открывает отправку."""

from datetime import datetime, timezone

from app.models.expertise import Expertise, ExpertiseStatus
from app.models.notification import Notification
from app.models.payment import Payment, PaymentStatus
from app.services.expertise.repo import ExpertiseRepository
from app.services.notifications.repo import NotificationRepository


class ApplyExpertisePaymentUseCase:
    """Сдвинуть статус экспертизы по успешному платежу и уведомить эксперта.

    Вызывается и из вебхука ЮKassa, и из кнопки «проверить оплату».
    Повторный вызов с тем же платежом ничего не меняет: статус уже сдвинут.
    """

    def __init__(
        self, expertises: ExpertiseRepository, notifications: NotificationRepository
    ) -> None:
        self.expertises = expertises
        self.notifications = notifications

    async def execute(self, payment: Payment) -> Expertise | None:
        """Вернуть обновлённую экспертизу или None, если платёж не про экспертизу или ещё не оплачен."""

        if payment.status != PaymentStatus.SUCCEEDED:
            return None

        expertise = await self.expertises.get_by_payment_id(payment.id)
        if expertise is None or expertise.expert_id is None:
            return None

        now = datetime.now(timezone.utc)

        if payment.id == expertise.advance_payment_id and expertise.status == ExpertiseStatus.CONTRACT:
            expertise.advance_paid_at = now
            expertise.status = ExpertiseStatus.IN_PROGRESS
            text = f"Заказчик оплатил аванс по заявке №{expertise.id}, можно приступать к работе"
        elif payment.id == expertise.final_payment_id and expertise.status == ExpertiseStatus.CONCLUSION_READY:
            expertise.final_paid_at = now
            expertise.status = ExpertiseStatus.PAID
            text = f"Заказчик оплатил остаток по заявке №{expertise.id}, отправьте заключение"
        else:
            return expertise

        self.notifications.add_all(
            [Notification(user_id=expertise.expert_id, expertise_id=expertise.id, text=text)]
        )

        return await self.expertises.save(expertise)
