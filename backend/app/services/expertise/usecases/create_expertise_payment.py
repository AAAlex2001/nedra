"""Шаги 7 и 9: заказчик оплачивает аванс или остаток по 50 %."""

from app.models.expertise import Expertise, ExpertiseStatus
from app.models.payment import Payment, PaymentStatus
from app.models.user import User
from app.services.contracts.executors import executor_for
from app.services.expertise.exceptions import (
    ExpertiseAccessError,
    ExpertiseStateError,
    PriceMissingError,
)
from app.services.expertise.money import split_price
from app.services.expertise.repo import ExpertiseRepository
from app.services.payments.repo import PaymentRepository
from app.services.payments.usecases.create_payment import CreatePaymentUseCase


class CreateExpertisePaymentUseCase:
    """Создать платёж ЮKassa на нужный этап и привязать его к экспертизе.

    Какой этап платить, решает статус: contract — аванс, conclusion_ready — остаток.
    Если для этапа уже есть неоплаченный платёж со ссылкой, возвращаем его,
    а не плодим новые. Касса принадлежит «Недрам», поэтому по договорам
    с другим исполнителем картой платить нельзя.
    """

    def __init__(
        self,
        expertises: ExpertiseRepository,
        payments: PaymentRepository,
        create_payment: CreatePaymentUseCase,
    ) -> None:
        self.expertises = expertises
        self.payments = payments
        self.create_payment = create_payment

    async def execute(self, customer: User, expertise: Expertise) -> Payment:
        """Вернуть платёж со ссылкой на оплату. Бросает ошибки экспертизы и PaymentGatewayError."""

        if expertise.customer_id != customer.id:
            raise ExpertiseAccessError("Оплатить может только заказчик этой заявки")

        if expertise.price is None:
            raise PriceMissingError("Стоимость экспертизы не задана")

        if not executor_for(expertise.contract_kind).card_payment:
            raise ExpertiseStateError("По этому договору оплата только по счёту исполнителя")

        advance, final = split_price(expertise.price)

        if expertise.status == ExpertiseStatus.CONTRACT:
            existing_id = expertise.advance_payment_id
            amount = advance
            description = f"Экспертиза №{expertise.id}: аванс 50%"
        elif expertise.status == ExpertiseStatus.CONCLUSION_READY:
            existing_id = expertise.final_payment_id
            amount = final
            description = f"Экспертиза №{expertise.id}: остаток 50%"
        else:
            raise ExpertiseStateError("Сейчас платить нечего")

        if existing_id is not None:
            existing = await self.payments.get_by_id(existing_id)
            if existing is not None and existing.status == PaymentStatus.PENDING:
                return existing

        payment = await self.create_payment.execute(customer, amount, description)

        if expertise.status == ExpertiseStatus.CONTRACT:
            expertise.advance_payment_id = payment.id
        else:
            expertise.final_payment_id = payment.id

        await self.expertises.save(expertise)

        return payment
