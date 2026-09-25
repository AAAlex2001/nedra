"""Админка: список зарегистрированных заказчиков со сводкой по заявкам."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.dependencies.admin import require_admin
from app.dependencies.users import get_user_repository
from app.models.expertise import Expertise, ExpertiseCompany
from app.models.user import UserRole
from app.schemas.user import CustomerOutSchema
from app.services.users.repo import UserRepository

router = APIRouter(
    prefix="/admin/customers",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


async def count_expertises(db: AsyncSession) -> dict[int, int]:
    """Сколько заявок подал каждый заказчик. Один запрос вместо обхода в цикле."""

    stmt = select(Expertise.customer_id, func.count()).group_by(Expertise.customer_id)
    result = await db.execute(stmt)

    return {customer_id: total for customer_id, total in result.all()}


async def load_companies(db: AsyncSession) -> dict[int, ExpertiseCompany]:
    """Организация из последней заявки каждого заказчика. Тоже одним запросом.

    Заявки идут от старых к новым, поэтому в словаре остаётся самая свежая.
    """

    stmt = (
        select(Expertise.customer_id, ExpertiseCompany)
        .join(ExpertiseCompany, ExpertiseCompany.expertise_id == Expertise.id)
        .order_by(Expertise.created_at)
    )
    result = await db.execute(stmt)

    return {customer_id: company for customer_id, company in result.all()}


@router.get("")
async def list_customers(
    users: UserRepository = Depends(get_user_repository),
    db: AsyncSession = Depends(get_session),
) -> list[CustomerOutSchema]:
    """Заказчики с организацией из последней заявки и числом заявок, новые сверху."""

    accounts = await users.list_by_role(UserRole.CUSTOMER)
    totals = await count_expertises(db)
    companies = await load_companies(db)

    customers: list[CustomerOutSchema] = []

    for account in accounts:
        company = companies.get(account.id)

        customers.append(
            CustomerOutSchema(
                user_id=account.id,
                email=account.email,
                full_name=account.full_name,
                phone=account.phone,
                created_at=account.created_at,
                company_name=company.name if company else None,
                company_inn=company.inn if company else None,
                expertises_count=totals.get(account.id, 0),
            )
        )

    return customers
