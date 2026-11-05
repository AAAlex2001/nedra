"""Просмотр оплаты аудита."""

from src.audit.models.audit_payment import AuditPayment
from src.audit.repositories.audit_payments import AuditPaymentRepository
from src.audit.site.audit_access import AuditAccess
from src.audit.site.schemas.audit_payments import (
    AuditPaymentsResponse,
    AuditPaymentStageResponse,
)
from src.billing.repositories.invoices import InvoiceRepository
from src.billing.schemas.invoice import InvoiceResponse
from src.payments.enums import PaymentStage
from src.payments.repositories.payments import PaymentRepository
from src.payments.schemas.payment import PaymentResponse
from src.users.models.user import User


class GetAuditPaymentsUseCase:
    """Оплата этапов и текущий счёт."""

    def __init__(
        self,
        *,
        access: AuditAccess,
        stages: AuditPaymentRepository,
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
        audit_id: int,
        user: User,
    ) -> AuditPaymentsResponse:
        """Получить сведения об оплате."""

        await self.access.get_visible(
            audit_id=audit_id,
            user=user,
        )
        advance = await self.stages.get(
            audit_id=audit_id,
            stage=PaymentStage.ADVANCE,
        )
        final = await self.stages.get(
            audit_id=audit_id,
            stage=PaymentStage.FINAL,
        )
        invoice = await self.invoices.get_unpaid_for_audit(audit_id=audit_id)
        invoice_response = None

        if invoice is not None:
            invoice_response = InvoiceResponse.from_model(invoice=invoice)

        advance_response = await self.get_stage_response(stage=advance)
        final_response = await self.get_stage_response(stage=final)

        return AuditPaymentsResponse(
            advance=advance_response,
            final=final_response,
            invoice=invoice_response,
        )

    async def get_stage_response(
        self, *, stage: AuditPayment | None
    ) -> AuditPaymentStageResponse | None:
        """Получить платёж и дату оплаты этапа."""

        if stage is None:
            return None

        payment_response = None

        if stage.payment_id is not None:
            payment = await self.payments.get_by_id(payment_id=stage.payment_id)

            if payment is not None:
                payment_response = PaymentResponse.from_model(payment=payment)

        return AuditPaymentStageResponse(
            paid_at=stage.paid_at,
            payment=payment_response,
        )
