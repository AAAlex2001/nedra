"""Обработка уведомления ЮKassa."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.audit_payment_confirmation import AuditPaymentConfirmation
from src.expertise.expertise_payment_confirmation import ExpertisePaymentConfirmation
from src.payments.payment_status_updater import PaymentStatusUpdater
from src.payments.repositories.payments import PaymentRepository


class ProcessPaymentWebhookUseCase:
    """Проверка уведомления и запись оплаты."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        payments: PaymentRepository,
        status_updater: PaymentStatusUpdater,
        audit_confirmation: AuditPaymentConfirmation,
        expertise_confirmation: ExpertisePaymentConfirmation,
    ) -> None:
        """Хранилище и сверка оплаты."""

        self.session = session
        self.payments = payments
        self.status_updater = status_updater
        self.audit_confirmation = audit_confirmation
        self.expertise_confirmation = expertise_confirmation

    async def execute(self, *, provider_payment_id: str) -> None:
        """Учесть подтверждённый платёж."""

        payment = await self.payments.get_for_update_by_provider_id(
            provider_payment_id=provider_payment_id,
        )

        if payment is None:
            return

        await self.status_updater.update_from_provider(payment=payment)
        await self.audit_confirmation.confirm_online_payment(payment=payment)
        await self.expertise_confirmation.confirm_online_payment(payment=payment)
        await self.session.commit()
