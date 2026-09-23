"""Реакция экспертизы на оплаченный платёж ЮKassa."""

from app.models.billing import InvoiceStage
from app.models.expertise import Expertise
from app.models.notification import Notification
from app.models.payment import Payment, PaymentStatus
from app.services.expertise.repo import ExpertiseRepository
from app.services.expertise.stages import mark_stage_paid, stage_notification_kind
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

        stage = self.stage_of(expertise, payment)
        if stage is None:
            return expertise

        text = mark_stage_paid(expertise, stage)
        if text is None:
            return expertise

        self.notifications.add_all(
            [
                Notification(
                    user_id=expertise.expert_id,
                    expertise_id=expertise.id,
                    kind=stage_notification_kind(expertise),
                    text=text,
                )
            ]
        )

        return await self.expertises.save(expertise)

    @staticmethod
    def stage_of(expertise: Expertise, payment: Payment) -> InvoiceStage | None:
        """За какой этап этот платёж."""

        if payment.id == expertise.advance_payment_id:
            return InvoiceStage.ADVANCE

        if payment.id == expertise.final_payment_id:
            return InvoiceStage.FINAL

        return None
