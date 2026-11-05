"""Изменение этапа после оплаты."""

from datetime import UTC, datetime
from decimal import Decimal

from src.audit.enums import AuditStatus
from src.audit.models.audit_payment import AuditPayment
from src.audit.repositories.audit_payments import AuditPaymentRepository
from src.audit.repositories.audits import AuditRepository
from src.notifications.models.notification import Notification
from src.notifications.repositories.notifications import NotificationRepository
from src.payments.amounts import stage_amount
from src.payments.enums import PaymentStage, PaymentStatus
from src.payments.exceptions import PaymentStateError
from src.payments.models.payment import Payment


class AuditPaymentConfirmation:
    """Учёт подтверждённой оплаты работы."""

    def __init__(
        self,
        *,
        audits: AuditRepository,
        stages: AuditPaymentRepository,
        notifications: NotificationRepository,
    ) -> None:
        """Работа, этапы и уведомления."""

        self.audits = audits
        self.stages = stages
        self.notifications = notifications

    async def confirm(
        self,
        *,
        audit_id: int,
        stage: PaymentStage,
        amount: Decimal,
        paid_at: datetime,
    ) -> None:
        """Записать оплату и открыть следующий этап."""

        audit = await self.audits.get_for_update(audit_id=audit_id)

        if audit is None or audit.lead_id is None:
            raise PaymentStateError("Работа или исполнитель не найдены")

        payment_stage = await self.stages.get(
            audit_id=audit_id,
            stage=stage,
        )

        if payment_stage is not None and payment_stage.paid_at is not None:
            return

        price = audit.agreed_price

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
            if audit.status != AuditStatus.CONTRACT:
                raise PaymentStateError("Сейчас аванс не ожидается")

            audit.status = AuditStatus.PLAN
            message = f"Аванс по работе №{audit_id} оплачен"
            notification_kind = None
        else:
            if audit.status != AuditStatus.CONCLUSION_READY:
                raise PaymentStateError("Окончательный расчёт ещё не открыт")

            audit.status = AuditStatus.PAID
            message = f"Работа №{audit_id} оплачена полностью, отправьте заключение"
            notification_kind = "sign_conclusion"

        if payment_stage is None:
            payment_stage = AuditPayment(
                audit_id=audit_id,
                stage=stage,
            )

        payment_stage.paid_at = paid_at
        await self.stages.save(payment_stage=payment_stage)
        await self.audits.save(audit=audit)
        await self.notifications.add(
            notification=Notification(
                user_id=audit.lead_id,
                audit_id=audit_id,
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

        audit_id, stage = payment_stage
        await self.confirm(
            audit_id=audit_id,
            stage=stage,
            amount=payment.amount,
            paid_at=payment.paid_at or datetime.now(UTC),
        )
