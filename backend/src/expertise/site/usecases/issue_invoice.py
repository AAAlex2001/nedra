"""Выставление счёта заказчику."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.billing.models.invoice import Invoice
from src.billing.repositories.invoices import InvoiceRepository
from src.billing.schemas.invoice import InvoiceResponse
from src.contracts.enums import CustomerType
from src.expertise.enums import ExpertiseStatus
from src.expertise.exceptions import ExpertiseNotFoundError, ExpertiseStateError
from src.expertise.repositories.expertise_customers import ExpertiseCustomerRepository
from src.expertise.repositories.expertises import ExpertiseRepository
from src.payments.amounts import stage_amount
from src.payments.enums import PaymentStage
from src.users.enums import UserRole
from src.users.models.user import User


class IssueExpertiseInvoiceUseCase:
    """Счёт на аванс или окончательный расчёт."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        expertises: ExpertiseRepository,
        customers: ExpertiseCustomerRepository,
        invoices: InvoiceRepository,
    ) -> None:
        """Работы, реквизиты и счета."""

        self.session = session
        self.expertises = expertises
        self.customers = customers
        self.invoices = invoices

    async def execute(
        self,
        *,
        expertise_id: int,
        user: User,
    ) -> InvoiceResponse:
        """Выставить счёт на текущий этап."""

        expertise = await self.expertises.get_for_update(expertise_id=expertise_id)
        if expertise is None or expertise.customer_id != user.id or user.role != UserRole.CUSTOMER:
            raise ExpertiseNotFoundError()

        if expertise.customer_type == CustomerType.INDIVIDUAL:
            raise ExpertiseStateError("Физические лица оплачивают работу картой")

        if expertise.status == ExpertiseStatus.CONTRACT:
            stage = PaymentStage.ADVANCE
        elif expertise.status == ExpertiseStatus.CONCLUSION_READY:
            stage = PaymentStage.FINAL
        else:
            raise ExpertiseStateError("Сейчас оплата не ожидается")

        if expertise.price is None:
            raise ExpertiseStateError("Стоимость работы не согласована")

        existing_invoice = await self.invoices.get_unpaid_for_expertise_stage(
            expertise_id=expertise_id,
            stage=stage,
        )
        if existing_invoice is not None:
            return InvoiceResponse.from_model(invoice=existing_invoice)

        company = await self.customers.get_company(expertise_id=expertise_id)
        if company is None:
            raise ExpertiseStateError("В заявке нет реквизитов заказчика")

        invoice = Invoice(
            expertise_id=expertise_id,
            stage=stage,
            amount=stage_amount(
                price=expertise.price,
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
