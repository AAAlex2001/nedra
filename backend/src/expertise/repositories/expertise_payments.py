"""Оплата этапов работы."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.expertise.models.expertise_payment import ExpertisePayment
from src.payments.enums import PaymentStage


class ExpertisePaymentRepository:
    """Аванс и окончательный расчёт."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def get(
        self,
        *,
        expertise_id: int,
        stage: PaymentStage,
    ) -> ExpertisePayment | None:
        """Получить оплату выбранного этапа."""

        return await self.session.get(ExpertisePayment, (expertise_id, stage))

    async def find_payment_stage(self, *, payment_id: int) -> tuple[int, PaymentStage] | None:
        """Найти работу и этап онлайн-платежа."""

        statement = select(ExpertisePayment.expertise_id, ExpertisePayment.stage).where(
            ExpertisePayment.payment_id == payment_id,
        )
        query_result = await self.session.execute(statement)
        payment_stage = query_result.one_or_none()

        if payment_stage is None:
            return None

        return payment_stage.expertise_id, PaymentStage(payment_stage.stage)

    async def save(self, *, payment_stage: ExpertisePayment) -> None:
        """Сохранить оплату этапа."""

        self.session.add(payment_stage)
        await self.session.flush()

    async def has_payments(self, *, expertise_id: int) -> bool:
        """Проверить наличие платёжной истории."""

        statement = (
            select(ExpertisePayment.expertise_id)
            .where(
                ExpertisePayment.expertise_id == expertise_id,
                (ExpertisePayment.payment_id.is_not(None))
                | (ExpertisePayment.paid_at.is_not(None)),
            )
            .limit(1)
        )

        return await self.session.scalar(statement) is not None
