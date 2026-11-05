"""Сводка работ заказчиков для администратора."""

from sqlalchemy import func, select, union_all
from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.models.audit import Audit
from src.audit.models.audit_company import AuditCompany
from src.expertise.models.expertise import Expertise
from src.expertise.models.expertise_company import ExpertiseCompany
from src.users.customer_company import CustomerCompany


class CustomerActivityRepository:
    """Счётчики работ и последние реквизиты."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def count_by_customers(self) -> dict[int, int]:
        """Посчитать аудиты и экспертизы заказчиков."""

        customer_works = union_all(
            select(Audit.customer_id),
            select(Expertise.customer_id),
        ).subquery()
        statement = select(customer_works.c.customer_id, func.count()).group_by(
            customer_works.c.customer_id
        )
        query_result = await self.session.execute(statement)

        return dict(query_result.all())

    async def get_latest_companies(self) -> dict[int, CustomerCompany]:
        """Получить последние реквизиты каждого заказчика."""

        companies = union_all(
            select(
                Audit.customer_id,
                Audit.created_at,
                Audit.id,
                AuditCompany.name,
                AuditCompany.inn,
            ).join(AuditCompany, AuditCompany.audit_id == Audit.id),
            select(
                Expertise.customer_id,
                Expertise.created_at,
                Expertise.id,
                ExpertiseCompany.name,
                ExpertiseCompany.inn,
            ).join(ExpertiseCompany, ExpertiseCompany.expertise_id == Expertise.id),
        ).subquery()
        statement = (
            select(companies)
            .distinct(companies.c.customer_id)
            .order_by(
                companies.c.customer_id,
                companies.c.created_at.desc(),
                companies.c.id.desc(),
            )
        )
        query_result = await self.session.execute(statement)

        return {
            company.customer_id: CustomerCompany(
                name=company.name,
                inn=company.inn,
            )
            for company in query_result
        }
