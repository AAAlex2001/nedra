"""Просмотр своего платежа."""

from src.payments.exceptions import PaymentNotFoundError
from src.payments.repositories.payments import PaymentRepository
from src.payments.schemas.payment import PaymentResponse


class GetPaymentUseCase:
    """Платёж текущего пользователя."""

    def __init__(self, *, payments: PaymentRepository) -> None:
        """Хранилище платежей."""

        self.payments = payments

    async def execute(
        self,
        *,
        payment_id: int,
        user_id: int,
    ) -> PaymentResponse:
        """Найти доступный платёж."""

        payment = await self.payments.get_for_user(
            payment_id=payment_id,
            user_id=user_id,
        )

        if payment is None:
            raise PaymentNotFoundError()

        return PaymentResponse.from_model(payment=payment)
