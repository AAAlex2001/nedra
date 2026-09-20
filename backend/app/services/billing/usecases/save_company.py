"""Сценарий сохранения реквизитов организации заказчика."""

from app.models.billing import CustomerCompany
from app.models.user import User
from app.schemas.billing import CompanyInSchema
from app.services.billing.repo import CustomerCompanyRepository
from app.services.billing.validators import normalize_inn, normalize_kpp


class SaveCustomerCompanyUseCase:
    """Записать реквизиты плательщика. Их печатаем в счёте и акте."""

    def __init__(self, companies: CustomerCompanyRepository) -> None:
        self.companies = companies

    async def execute(self, user: User, data: CompanyInSchema) -> CustomerCompany:
        """Создать или обновить реквизиты. Бросает InvalidCompanyError."""

        inn = normalize_inn(data.inn)
        kpp = normalize_kpp(data.kpp)

        company = await self.companies.get_by_user(user.id)
        if company is None:
            company = CustomerCompany(user_id=user.id)

        company.name = data.name.strip()
        company.inn = inn
        company.kpp = kpp
        company.address = data.address.strip()

        return await self.companies.save(company)
