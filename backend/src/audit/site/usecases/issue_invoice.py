"""Выставление счёта заказчику."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.enums import AuditStatus
from src.audit.exceptions import AuditNotFoundError, AuditStateError
from src.audit.repositories.audit_customers import AuditCustomerRepository
from src.audit.repositories.audits import AuditRepository
from src.billing.models.invoice import Invoice
from src.billing.repositories.invoices import InvoiceRepository
from src.billing.schemas.invoice import InvoiceResponse
from src.contracts.enums import CustomerType
from src.payments.amounts import stage_amount
from src.payments.enums import PaymentStage
from src.users.enums import UserRole
from src.users.models.user import User


class IssueAuditInvoiceUseCase:
    """Счёт на аванс или окончательный расчёт."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        audits: AuditRepository,
        customers: AuditCustomerRepository,
        invoices: InvoiceRepository,
    ) -> None:
        """Работы, реквизиты и счета."""

        self.session = session
        self.audits = audits
        self.customers = customers
        self.invoices = invoices

    async def execute(
        self,
        *,
        audit_id: int,
        user: User,
    ) -> InvoiceResponse:
        """Выставить счёт на текущий этап."""

        audit = await self.audits.get_for_update(audit_id=audit_id)
        if audit is None or audit.customer_id != user.id or user.role != UserRole.CUSTOMER:
            raise AuditNotFoundError()

        if audit.customer_type == CustomerType.INDIVIDUAL:
            raise AuditStateError("Физические лица оплачивают работу картой")

        if audit.status == AuditStatus.CONTRACT:
            stage = PaymentStage.ADVANCE
        elif audit.status == AuditStatus.CONCLUSION_READY:
            stage = PaymentStage.FINAL
        else:
            raise AuditStateError("Сейчас оплата не ожидается")

        if audit.agreed_price is None:
            raise AuditStateError("Стоимость работы не согласована")

        existing_invoice = await self.invoices.get_unpaid_for_audit_stage(
            audit_id=audit_id,
            stage=stage,
        )
        if existing_invoice is not None:
            return InvoiceResponse.from_model(invoice=existing_invoice)

        company = await self.customers.get_company(audit_id=audit_id)
        if company is None:
            raise AuditStateError("В заявке нет реквизитов заказчика")

        invoice = Invoice(
            audit_id=audit_id,
            stage=stage,
            amount=stage_amount(
                price=audit.agreed_price,
                stage=stage,
            ),
            payer_name=company.name,
            payer_inn=company.inn,
            payer_kpp=company.kpp,
            payer_address=company.address,
        )
        await self.invoices.save(invoice=invoice)
        response = InvoiceResponse.from_model(invoice=invoice)
        await self.session.commit()
        return response
