"""Изменение этапа после оплаты."""

from datetime import UTC, datetime
from decimal import Decimal

from src.expertise.enums import ExpertiseStatus
from src.expertise.models.expertise_payment import ExpertisePayment
from src.expertise.repositories.expertise_payments import ExpertisePaymentRepository
from src.expertise.repositories.expertises import ExpertiseRepository
from src.notifications.models.notification import Notification
from src.notifications.repositories.notifications import NotificationRepository
from src.payments.amounts import stage_amount
from src.payments.enums import PaymentStage, PaymentStatus
from src.payments.exceptions import PaymentStateError
from src.payments.models.payment import Payment


class ExpertisePaymentConfirmation:
    """Учёт подтверждённой оплаты работы."""

    def __init__(
        self,
        *,
        expertises: ExpertiseRepository,
        stages: ExpertisePaymentRepository,
        notifications: NotificationRepository,
    ) -> None:
        """Работа, этапы и уведомления."""

        self.expertises = expertises
        self.stages = stages
        self.notifications = notifications

    async def confirm(
        self,
        *,
        expertise_id: int,
        stage: PaymentStage,
        amount: Decimal,
        paid_at: datetime,
    ) -> None:
        """Записать оплату и открыть следующий этап."""

        expertise = await self.expertises.get_for_update(expertise_id=expertise_id)

        if expertise is None or expertise.expert_id is None:
            raise PaymentStateError("Работа или исполнитель не найдены")

        payment_stage = await self.stages.get(
            expertise_id=expertise_id,
            stage=stage,
        )

        if payment_stage is not None and payment_stage.paid_at is not None:
            return

        price = expertise.price

        if (
            price is None
            or stage_amount(
                price=price,
                stage=stage,
            )
            != amount
        ):
            raise PaymentStateError("Сумма платежа не совпадает со стоимостью этапа")

        if stage == PaymentStage.ADVANCE:
            if expertise.status != ExpertiseStatus.CONTRACT:
                raise PaymentStateError("Сейчас аванс не ожидается")

            expertise.status = ExpertiseStatus.IN_PROGRESS
            message = f"Аванс по работе №{expertise_id} оплачен"
            notification_kind = None
        else:
            if expertise.status != ExpertiseStatus.CONCLUSION_READY:
                raise PaymentStateError("Окончательный расчёт ещё не открыт")

            expertise.status = ExpertiseStatus.PAID
            message = f"Работа №{expertise_id} оплачена полностью, отправьте заключение"
            notification_kind = "sign_conclusion"

        if payment_stage is None:
            payment_stage = ExpertisePayment(
                expertise_id=expertise_id,
                stage=stage,
            )

        payment_stage.paid_at = paid_at
        await self.stages.save(payment_stage=payment_stage)
        await self.expertises.save(expertise=expertise)
        await self.notifications.add(
            notification=Notification(
                user_id=expertise.expert_id,
                expertise_id=expertise_id,
                kind=notification_kind,
                text=message,
            ),
        )

    async def confirm_online_payment(self, *, payment: Payment) -> None:
        """Учесть успешный платёж провайдера."""

        if payment.status != PaymentStatus.SUCCEEDED:
            return

        payment_stage = await self.stages.find_payment_stage(payment_id=payment.id)

        if payment_stage is None:
            return

        expertise_id, stage = payment_stage
        await self.confirm(
            expertise_id=expertise_id,
            stage=stage,
            amount=payment.amount,
            paid_at=payment.paid_at or datetime.now(UTC),
        )
