"""Сценарий создания платежа."""

from decimal import Decimal
from uuid import uuid4

from app.models.payment import Payment
from app.models.user import User
from app.services.payments.gateway import YooKassaGateway
from app.services.payments.repo import PaymentRepository


class CreatePaymentUseCase:
    """Создать платёж в ЮKassa и сохранить его у себя.

    Сначала идём в ЮKassa, потом пишем в БД: если ЮKassa не ответила,
    у нас не остаётся «пустого» платежа. Если упала запись в БД, в ЮKassa
    останется неоплаченный платёж, который никто не откроет — это безопасно.
    """

    def __init__(
        self,
        payments: PaymentRepository,
        gateway: YooKassaGateway,
        return_url: str,
    ) -> None:
        self.payments = payments
        self.gateway = gateway
        self.return_url = return_url

    async def execute(self, user: User, amount: Decimal, description: str) -> Payment:
        """Вернуть платёж со ссылкой на оплату. Бросает PaymentGatewayError."""

        idempotence_key = str(uuid4())

        gateway_payment = await self.gateway.create_payment(
            amount=amount,
            description=description,
            return_url=self.return_url,
            idempotence_key=idempotence_key,
        )

        payment = Payment(
            user_id=user.id,
            amount=amount,
            description=description,
            status=gateway_payment.status,
            provider_payment_id=gateway_payment.id,
            confirmation_url=gateway_payment.confirmation_url,
        )

        return await self.payments.add(payment)
