"""Сверка оплаты с провайдером."""

from datetime import UTC, datetime

from src.payments.enums import PaymentStatus
from src.payments.exceptions import PaymentGatewayError
from src.payments.gateway import YooKassaGateway
from src.payments.models.payment import Payment
from src.payments.repositories.payments import PaymentRepository


class PaymentStatusUpdater:
    """Сверка платежа с ЮKassa."""

    def __init__(
        self,
        *,
        payments: PaymentRepository,
        gateway: YooKassaGateway,
    ) -> None:
        """Провайдер и платежи."""

        self.payments = payments
        self.gateway = gateway

    async def update_from_provider(self, *, payment: Payment) -> None:
        """Проверить реквизиты и обновить состояние платежа."""

        provider_payment = await self.gateway.get_payment(
            provider_payment_id=payment.provider_payment_id,
        )

        if (
            provider_payment.id != payment.provider_payment_id
            or provider_payment.amount.value != payment.amount
            or provider_payment.amount.currency != payment.currency
            or (provider_payment.status == PaymentStatus.SUCCEEDED and not provider_payment.paid)
        ):
            raise PaymentGatewayError()

        if payment.status not in (PaymentStatus.SUCCEEDED, PaymentStatus.CANCELED):
            payment.status = provider_payment.status

        if payment.status == PaymentStatus.SUCCEEDED:
            payment.paid_at = payment.paid_at or datetime.now(UTC)
            payment.confirmation_url = None
        elif payment.status == PaymentStatus.CANCELED:
            payment.confirmation_url = None

        await self.payments.save(payment=payment)
