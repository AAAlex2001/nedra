"""Сценарий синхронизации статуса платежа с ЮKassa."""

from datetime import datetime, timezone

from app.models.payment import Payment, PaymentStatus
from app.services.payments.exceptions import PaymentNotFoundError
from app.services.payments.gateway import YooKassaGateway
from app.services.payments.repo import PaymentRepository


class SyncPaymentStatusUseCase:
    """Спросить у ЮKassa актуальный статус и записать его к себе.

    Используется и для уведомлений от ЮKassa, и для кнопки «проверить оплату»
    на фронте. В обоих случаях мы не верим входящим данным, а запрашиваем
    платёж через API по его id — подделать такой ответ нельзя.
    """

    def __init__(self, payments: PaymentRepository, gateway: YooKassaGateway) -> None:
        self.payments = payments
        self.gateway = gateway

    async def execute(self, provider_payment_id: str) -> Payment:
        """Вернуть обновлённый платёж. Бросает PaymentNotFoundError и PaymentGatewayError."""

        payment = await self.payments.get_by_provider_id(provider_payment_id)
        if payment is None:
            raise PaymentNotFoundError(f"Платёж {provider_payment_id} не найден")

        gateway_payment = await self.gateway.get_payment(provider_payment_id)

        if gateway_payment.status == payment.status:
            return payment

        payment.status = gateway_payment.status

        if gateway_payment.status == PaymentStatus.SUCCEEDED:
            payment.paid_at = datetime.now(timezone.utc)
            payment.confirmation_url = None

        if gateway_payment.status == PaymentStatus.CANCELED:
            payment.confirmation_url = None

        return await self.payments.save(payment)
