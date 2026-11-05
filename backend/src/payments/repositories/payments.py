"""Платежи пользователей."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.payments.models.payment import Payment


class PaymentRepository:
    """Поиск и сохранение платежей."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def get_by_id(self, *, payment_id: int) -> Payment | None:
        """Найти платёж по номеру."""

        return await self.session.get(Payment, payment_id)

    async def get_for_user(
        self,
        *,
        payment_id: int,
        user_id: int,
    ) -> Payment | None:
        """Найти платёж пользователя."""

        statement = select(Payment).where(
            Payment.id == payment_id,
            Payment.user_id == user_id,
        )

        return await self.session.scalar(statement)

    async def get_for_update(self, *, payment_id: int) -> Payment | None:
        """Получить платёж для изменения."""

        statement = select(Payment).where(Payment.id == payment_id).with_for_update()

        return await self.session.scalar(statement)

    async def get_for_update_by_provider_id(self, *, provider_payment_id: str) -> Payment | None:
        """Найти платёж для обновления статуса."""

        statement = (
            select(Payment)
            .where(Payment.provider_payment_id == provider_payment_id)
            .with_for_update()
        )

        return await self.session.scalar(statement)

    async def save(self, *, payment: Payment) -> None:
        """Сохранить платёж."""

        self.session.add(payment)
        await self.session.flush()
