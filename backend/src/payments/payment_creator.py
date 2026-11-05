"""Создание платежа у провайдера и в базе."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import NAMESPACE_URL, uuid4, uuid5

from src.payments.enums import PaymentStatus
from src.payments.exceptions import PaymentGatewayError
from src.payments.gateway import YooKassaGateway
from src.payments.models.payment import Payment
from src.payments.options import PAYMENT_CURRENCY
from src.payments.repositories.payments import PaymentRepository


class PaymentCreator:
    """Подготовка платежа и ссылки на оплату."""

    def __init__(
        self,
        *,
        payments: PaymentRepository,
        gateway: YooKassaGateway,
        return_url: str,
    ) -> None:
        """Провайдер и хранилище платежей."""

        self.payments = payments
        self.gateway = gateway
        self.return_url = return_url

    async def create(
        self,
        *,
        user_id: int,
        customer_email: str,
        amount: Decimal,
        description: str,
        operation_key: str | None = None,
    ) -> Payment:
        """Создать платёж без завершения транзакции."""

        idempotence_key = str(uuid4())

        if operation_key is not None:
            idempotence_key = str(uuid5(NAMESPACE_URL, f"{self.return_url}:{operation_key}"))

        provider_payment = await self.gateway.create_payment(
            amount=amount,
            description=description,
            customer_email=customer_email,
            return_url=self.return_url,
            idempotence_key=idempotence_key,
        )

        if (
            provider_payment.amount.value != amount
            or provider_payment.amount.currency != PAYMENT_CURRENCY
            or (provider_payment.status == PaymentStatus.SUCCEEDED and not provider_payment.paid)
        ):
            raise PaymentGatewayError()

        payment = Payment(
            user_id=user_id,
            amount=amount,
            description=description,
            currency=PAYMENT_CURRENCY,
            status=provider_payment.status,
            provider_payment_id=provider_payment.id,
            confirmation_url=provider_payment.confirmation_url,
        )
        if payment.status == PaymentStatus.SUCCEEDED:
            payment.paid_at = datetime.now(UTC)
            payment.confirmation_url = None
        elif payment.status == PaymentStatus.CANCELED:
            payment.confirmation_url = None

        await self.payments.save(payment=payment)

        return payment
