"""Проверка оплаты пользователем."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.audit_payment_confirmation import AuditPaymentConfirmation
from src.expertise.expertise_payment_confirmation import ExpertisePaymentConfirmation
from src.payments.exceptions import PaymentNotFoundError
from src.payments.payment_status_updater import PaymentStatusUpdater
from src.payments.repositories.payments import PaymentRepository
from src.payments.schemas.payment import PaymentResponse


class RefreshPaymentUseCase:
    """Актуальное состояние своего платежа."""

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

    async def execute(
        self,
        *,
        payment_id: int,
        user_id: int,
    ) -> PaymentResponse:
        """Проверить оплату у провайдера."""

        payment = await self.payments.get_for_update(payment_id=payment_id)

        if payment is None or payment.user_id != user_id:
            raise PaymentNotFoundError()

        await self.status_updater.update_from_provider(payment=payment)
        await self.audit_confirmation.confirm_online_payment(payment=payment)
        await self.expertise_confirmation.confirm_online_payment(payment=payment)
        response = PaymentResponse.from_model(payment=payment)
        await self.session.commit()

        return response
