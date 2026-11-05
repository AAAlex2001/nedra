"""Оплата этапов работы."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.models.audit_payment import AuditPayment
from src.payments.enums import PaymentStage


class AuditPaymentRepository:
    """Аванс и окончательный расчёт."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def get(
        self,
        *,
        audit_id: int,
        stage: PaymentStage,
    ) -> AuditPayment | None:
        """Получить оплату выбранного этапа."""

        return await self.session.get(AuditPayment, (audit_id, stage))

    async def find_payment_stage(self, *, payment_id: int) -> tuple[int, PaymentStage] | None:
        """Найти работу и этап онлайн-платежа."""

        statement = select(AuditPayment.audit_id, AuditPayment.stage).where(
            AuditPayment.payment_id == payment_id,
        )
        query_result = await self.session.execute(statement)
        payment_stage = query_result.one_or_none()

        if payment_stage is None:
            return None

        return payment_stage.audit_id, PaymentStage(payment_stage.stage)

    async def save(self, *, payment_stage: AuditPayment) -> None:
        """Сохранить оплату этапа."""

        self.session.add(payment_stage)
        await self.session.flush()

    async def has_payments(self, *, audit_id: int) -> bool:
        """Проверить наличие платёжной истории."""

        statement = (
            select(AuditPayment.audit_id)
            .where(
                AuditPayment.audit_id == audit_id,
                (AuditPayment.payment_id.is_not(None)) | (AuditPayment.paid_at.is_not(None)),
            )
            .limit(1)
        )

        return await self.session.scalar(statement) is not None
