"""Сценарий выставления счёта на оплату этапа экспертизы."""

from app.models.billing import Invoice, InvoiceStage
from app.models.expertise import Expertise
from app.models.user import User
from app.services.billing.exceptions import CompanyRequiredError
from app.services.billing.repo import InvoiceRepository
from app.services.expertise.exceptions import (
    ExpertiseAccessError,
    ExpertiseStateError,
    PriceMissingError,
)
from app.services.expertise.money import split_price
from app.services.expertise.stages import current_stage


class IssueInvoiceUseCase:
    """Выставить счёт на текущий этап: аванс или остаток.

    Плательщик — организация из заявки. Реквизиты копируются в счёт:
    выставленный документ не меняется. Пока счёт не оплачен, повторный
    запрос отдаёт тот же документ, а не плодит новые номера.
    """

    def __init__(self, invoices: InvoiceRepository) -> None:
        self.invoices = invoices

    async def execute(self, customer: User, expertise: Expertise) -> Invoice:
        """Бросает ExpertiseAccessError, ExpertiseStateError, PriceMissingError, CompanyRequiredError."""

        if expertise.customer_id != customer.id:
            raise ExpertiseAccessError("Счёт выставляется заказчику этой заявки")

        if expertise.price is None:
            raise PriceMissingError("Стоимость экспертизы не задана")

        stage = current_stage(expertise)
        if stage is None:
            raise ExpertiseStateError("Сейчас платить нечего")

        company = expertise.company
        if company is None:
            raise CompanyRequiredError("В заявке нет реквизитов заказчика")

        existing = await self.invoices.get_unpaid_for_stage(expertise.id, stage)
        if existing is not None:
            return existing

        advance, final = split_price(expertise.price)
        amount = advance if stage == InvoiceStage.ADVANCE else final

        invoice = Invoice(
            expertise_id=expertise.id,
            stage=stage,
            amount=amount,
            payer_name=company.name,
            payer_inn=company.inn,
            payer_kpp=company.kpp,
            payer_address=company.address,
        )

        return await self.invoices.add(invoice)
