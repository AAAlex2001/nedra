"""Оплата экспертизы картой."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.contracts.enums import CustomerType
from src.expertise.enums import ExpertiseStatus
from src.expertise.exceptions import ExpertiseNotFoundError, ExpertiseStateError
from src.expertise.expertise_payment_confirmation import ExpertisePaymentConfirmation
from src.expertise.models.expertise_payment import ExpertisePayment
from src.expertise.repositories.expertise_payments import ExpertisePaymentRepository
from src.expertise.repositories.expertises import ExpertiseRepository
from src.payments.amounts import stage_amount
from src.payments.enums import PaymentStage, PaymentStatus
from src.payments.options import STAGE_TITLES
from src.payments.payment_creator import PaymentCreator
from src.payments.repositories.payments import PaymentRepository
from src.payments.schemas.payment import PaymentResponse
from src.users.models.user import User


class CreateExpertisePaymentUseCase:
    """Платёж на текущий этап экспертизы."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        expertises: ExpertiseRepository,
        stages: ExpertisePaymentRepository,
        payments: PaymentRepository,
        creator: PaymentCreator,
        confirmation: ExpertisePaymentConfirmation,
    ) -> None:
        """Экспертизы, этапы и оплата."""

        self.session = session
        self.expertises = expertises
        self.stages = stages
        self.payments = payments
        self.creator = creator
        self.confirmation = confirmation

    async def execute(
        self,
        *,
        expertise_id: int,
        user: User,
    ) -> PaymentResponse:
        """Подготовить оплату картой."""

        expertise = await self.expertises.get_for_update(expertise_id=expertise_id)

        if expertise is None or expertise.customer_id != user.id:
            raise ExpertiseNotFoundError()

        if expertise.customer_type != CustomerType.INDIVIDUAL:
            raise ExpertiseStateError("Организации и предприниматели оплачивают работу по счёту")

        if expertise.status == ExpertiseStatus.CONTRACT:
            stage = PaymentStage.ADVANCE
        elif expertise.status == ExpertiseStatus.CONCLUSION_READY:
            stage = PaymentStage.FINAL
        else:
            raise ExpertiseStateError("Сейчас оплата не ожидается")

        if expertise.price is None:
            raise ExpertiseStateError("Стоимость работы не согласована")

        payment_stage = await self.stages.get(
            expertise_id=expertise_id,
            stage=stage,
        )

        previous_payment_id = 0

        if payment_stage is not None and payment_stage.payment_id is not None:
            previous_payment_id = payment_stage.payment_id
            previous_payment = await self.payments.get_by_id(payment_id=payment_stage.payment_id)

            if previous_payment is not None and previous_payment.status != PaymentStatus.CANCELED:
                return PaymentResponse.from_model(payment=previous_payment)

        payment = await self.creator.create(
            user_id=user.id,
            customer_email=user.email,
            amount=stage_amount(
                price=expertise.price,
                stage=stage,
            ),
            description=f"Экспертиза №{expertise_id}: {STAGE_TITLES[stage]}",
            operation_key=f"expertise:{expertise_id}:{stage}:after:{previous_payment_id}",
        )

        if payment_stage is None:
            payment_stage = ExpertisePayment(
                expertise_id=expertise_id,
                stage=stage,
            )

        payment_stage.payment_id = payment.id
        await self.stages.save(payment_stage=payment_stage)
        await self.confirmation.confirm_online_payment(payment=payment)
        response = PaymentResponse.from_model(payment=payment)
        await self.session.commit()

        return response
