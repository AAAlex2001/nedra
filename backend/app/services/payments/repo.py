"""Репозиторий платежей: только запросы к таблице payments."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment


class PaymentRepository:
    """Доступ к таблице payments. Сессию получает снаружи, коммитит сам."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_for_user(self, payment_id: int, user_id: int) -> Payment | None:
        """Платёж по id, но только если он принадлежит пользователю."""

        stmt = select(Payment).where(Payment.id == payment_id, Payment.user_id == user_id)
        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_by_provider_id(self, provider_payment_id: str) -> Payment | None:
        """Платёж по id из ЮKassa. Так мы находим его при обработке уведомления."""

        stmt = select(Payment).where(Payment.provider_payment_id == provider_payment_id)
        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def add(self, payment: Payment) -> Payment:
        """Сохранить новый платёж."""

        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)

        return payment

    async def save(self, payment: Payment) -> Payment:
        """Сохранить изменения уже существующего платежа."""

        await self.db.commit()
        await self.db.refresh(payment)

        return payment
