"""Чтение счетов."""

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.models.audit import Audit
from src.billing.models.invoice import Invoice
from src.expertise.models.expertise import Expertise
from src.payments.enums import PaymentStage


class InvoiceRepository:
    """Поиск счетов по работе."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def get_unpaid_for_expertise(self, *, expertise_id: int) -> Invoice | None:
        """Найти последний неоплаченный счёт экспертизы."""

        statement = (
            select(Invoice)
            .where(Invoice.expertise_id == expertise_id, Invoice.paid_at.is_(None))
            .order_by(Invoice.id.desc())
            .limit(1)
        )
        return await self.session.scalar(statement)

    async def get_unpaid_for_audit(self, *, audit_id: int) -> Invoice | None:
        """Найти последний неоплаченный счёт аудита."""

        statement = (
            select(Invoice)
            .where(Invoice.audit_id == audit_id, Invoice.paid_at.is_(None))
            .order_by(Invoice.id.desc())
            .limit(1)
        )
        return await self.session.scalar(statement)

    async def has_for_audit(self, *, audit_id: int) -> bool:
        """Проверить наличие счетов работы."""

        statement = select(Invoice.id).where(Invoice.audit_id == audit_id).limit(1)

        return await self.session.scalar(statement) is not None

    async def has_for_expertise(self, *, expertise_id: int) -> bool:
        """Проверить наличие счетов работы."""

        statement = select(Invoice.id).where(Invoice.expertise_id == expertise_id).limit(1)

        return await self.session.scalar(statement) is not None

    async def get_by_id(self, *, invoice_id: int) -> Invoice | None:
        """Найти счёт по номеру."""

        return await self.session.get(Invoice, invoice_id)

    async def get_for_update(self, *, invoice_id: int) -> Invoice | None:
        """Получить счёт для изменения."""

        statement = select(Invoice).where(Invoice.id == invoice_id).with_for_update()
        return await self.session.scalar(statement)

    async def belongs_to_customer(
        self,
        *,
        invoice_id: int,
        user_id: int,
    ) -> bool:
        """Проверить заказчика счёта."""

        statement = (
            select(Invoice.id)
            .outerjoin(Audit, Audit.id == Invoice.audit_id)
            .outerjoin(Expertise, Expertise.id == Invoice.expertise_id)
            .where(
                Invoice.id == invoice_id,
                or_(Audit.customer_id == user_id, Expertise.customer_id == user_id),
            )
        )
        return await self.session.scalar(statement) is not None

    async def get_executor_id(self, *, invoice_id: int) -> int | None:
        """Получить исполнителя оплачиваемой работы."""

        statement = (
            select(func.coalesce(Audit.lead_id, Expertise.expert_id))
            .select_from(Invoice)
            .outerjoin(Audit, Audit.id == Invoice.audit_id)
            .outerjoin(Expertise, Expertise.id == Invoice.expertise_id)
            .where(Invoice.id == invoice_id)
        )
        return await self.session.scalar(statement)

    async def list_for_customer(self, *, user_id: int) -> list[Invoice]:
        """Получить счета заказчика."""

        statement = (
            select(Invoice)
            .outerjoin(Audit, Audit.id == Invoice.audit_id)
            .outerjoin(Expertise, Expertise.id == Invoice.expertise_id)
            .where(or_(Audit.customer_id == user_id, Expertise.customer_id == user_id))
            .order_by(Invoice.created_at.desc(), Invoice.id.desc())
        )
        invoices = await self.session.scalars(statement)
        return list(invoices)

    async def list_all(self) -> list[Invoice]:
        """Получить все счета."""

        statement = select(Invoice).order_by(Invoice.created_at.desc(), Invoice.id.desc())
        invoices = await self.session.scalars(statement)
        return list(invoices)

    async def save(self, *, invoice: Invoice) -> None:
        """Сохранить счёт."""

        self.session.add(invoice)
        await self.session.flush()

    async def get_unpaid_for_audit_stage(
        self,
        *,
        audit_id: int,
        stage: PaymentStage,
    ) -> Invoice | None:
        """Найти неоплаченный счёт этапа."""

        statement = (
            select(Invoice)
            .where(
                Invoice.audit_id == audit_id,
                Invoice.stage == stage,
                Invoice.paid_at.is_(None),
            )
            .order_by(Invoice.id.desc())
            .limit(1)
        )

        return await self.session.scalar(statement)

    async def get_unpaid_for_expertise_stage(
        self,
        *,
        expertise_id: int,
        stage: PaymentStage,
    ) -> Invoice | None:
        """Найти неоплаченный счёт этапа."""

        statement = (
            select(Invoice)
            .where(
                Invoice.expertise_id == expertise_id,
                Invoice.stage == stage,
                Invoice.paid_at.is_(None),
            )
            .order_by(Invoice.id.desc())
            .limit(1)
        )

        return await self.session.scalar(statement)
