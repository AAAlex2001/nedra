"""Просмотр оплаты экспертизы."""

from src.billing.repositories.invoices import InvoiceRepository
from src.billing.schemas.invoice import InvoiceResponse
from src.expertise.models.expertise_payment import ExpertisePayment
from src.expertise.repositories.expertise_payments import ExpertisePaymentRepository
from src.expertise.site.expertise_access import ExpertiseAccess
from src.expertise.site.schemas.expertise_payments import (
    ExpertisePaymentsResponse,
    ExpertisePaymentStageResponse,
)
from src.payments.enums import PaymentStage
from src.payments.repositories.payments import PaymentRepository
from src.payments.schemas.payment import PaymentResponse
from src.users.models.user import User


class GetExpertisePaymentsUseCase:
    """Оплата этапов и текущий счёт."""

    def __init__(
        self,
        *,
        access: ExpertiseAccess,
        stages: ExpertisePaymentRepository,
        payments: PaymentRepository,
        invoices: InvoiceRepository,
    ) -> None:
        """Права доступа, этапы, платежи и счета."""

        self.access = access
        self.stages = stages
        self.payments = payments
        self.invoices = invoices

    async def execute(
        self,
        *,
        expertise_id: int,
        user: User,
    ) -> ExpertisePaymentsResponse:
        """Получить сведения об оплате."""

        await self.access.get_visible(
            expertise_id=expertise_id,
            user=user,
        )
        advance = await self.stages.get(
            expertise_id=expertise_id,
            stage=PaymentStage.ADVANCE,
        )
        final = await self.stages.get(
            expertise_id=expertise_id,
            stage=PaymentStage.FINAL,
        )
        invoice = await self.invoices.get_unpaid_for_expertise(expertise_id=expertise_id)
        invoice_response = None

        if invoice is not None:
            invoice_response = InvoiceResponse.from_model(invoice=invoice)

        advance_response = await self.get_stage_response(stage=advance)
        final_response = await self.get_stage_response(stage=final)

        return ExpertisePaymentsResponse(
            advance=advance_response,
            final=final_response,
            invoice=invoice_response,
        )

    async def get_stage_response(
        self, *, stage: ExpertisePayment | None
    ) -> ExpertisePaymentStageResponse | None:
        """Получить платёж и дату оплаты этапа."""

        if stage is None:
            return None

        payment_response = None

        if stage.payment_id is not None:
            payment = await self.payments.get_by_id(payment_id=stage.payment_id)

            if payment is not None:
                payment_response = PaymentResponse.from_model(payment=payment)

        return ExpertisePaymentStageResponse(
            paid_at=stage.paid_at,
            payment=payment_response,
        )
