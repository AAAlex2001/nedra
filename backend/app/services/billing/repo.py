"""Репозитории биллинга: реквизиты заказчиков и счета."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.billing import CustomerCompany, Invoice
from app.models.expertise import Expertise


class CustomerCompanyRepository:
    """Доступ к таблице customer_companies. Сессию получает снаружи, коммитит сам."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_user(self, user_id: int) -> CustomerCompany | None:
        """Реквизиты заказчика или None, если он их не заполнял."""

        return await self.db.get(CustomerCompany, user_id)

    async def save(self, company: CustomerCompany) -> CustomerCompany:
        """Сохранить новые или изменённые реквизиты."""

        self.db.add(company)
        await self.db.commit()
        await self.db.refresh(company)

        return company


class InvoiceRepository:
    """Доступ к таблице invoices."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, invoice_id: int) -> Invoice | None:
        """Счёт по id или None."""

        return await self.db.get(Invoice, invoice_id)

    async def get_unpaid_for_stage(self, expertise_id: int, stage: str) -> Invoice | None:
        """Неоплаченный счёт за этот этап, чтобы не выставлять второй такой же."""

        stmt = select(Invoice).where(
            Invoice.expertise_id == expertise_id,
            Invoice.stage == stage,
            Invoice.paid_at.is_(None),
        )
        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def list_for_customer(self, customer_id: int) -> list[Invoice]:
        """Счета заказчика, новые первыми."""

        stmt = (
            select(Invoice)
            .join(Expertise, Expertise.id == Invoice.expertise_id)
            .where(Expertise.customer_id == customer_id)
            .order_by(Invoice.created_at.desc())
        )
        result = await self.db.execute(stmt)

        return list(result.scalars().all())

    async def list_all(self) -> list[Invoice]:
        """Все счета для админки, новые первыми."""

        stmt = select(Invoice).order_by(Invoice.created_at.desc())
        result = await self.db.execute(stmt)

        return list(result.scalars().all())

    async def add(self, invoice: Invoice) -> Invoice:
        """Сохранить новый счёт."""

        self.db.add(invoice)
        await self.db.commit()
        await self.db.refresh(invoice)

        return invoice

    async def save(self, invoice: Invoice) -> Invoice:
        """Сохранить изменения счёта и всё, что сценарий добавил в сессию."""

        await self.db.commit()
        await self.db.refresh(invoice)

        return invoice
