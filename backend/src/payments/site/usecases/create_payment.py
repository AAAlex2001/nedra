"""Создание платежа пользователя."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.payments.payment_creator import PaymentCreator
from src.payments.site.schemas.create_payment import (
    CreatePaymentRequest,
    CreatePaymentResponse,
)
from src.users.models.user import User


class CreatePaymentUseCase:
    """Оплата с переходом к провайдеру."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        creator: PaymentCreator,
    ) -> None:
        """Создание и сохранение платежа."""

        self.session = session
        self.creator = creator

    async def execute(
        self,
        *,
        user: User,
        payload: CreatePaymentRequest,
    ) -> CreatePaymentResponse:
        """Создать платёж и вернуть ссылку."""

        payment = await self.creator.create(
            user_id=user.id,
            customer_email=user.email,
            amount=payload.amount,
            description=payload.description,
        )
        response = CreatePaymentResponse.from_model(payment=payment)
        await self.session.commit()

        return response
