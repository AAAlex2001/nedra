"""Просмотр заказчика аудита."""

from src.audit.repositories.audit_customers import AuditCustomerRepository
from src.audit.schemas.audit_company import AuditCompanyResponse
from src.audit.schemas.audit_participants import AuditCustomerResponse
from src.audit.site.audit_access import AuditAccess
from src.users.exceptions import UserNotFoundError
from src.users.models.user import User
from src.users.repositories.users import UserRepository


class GetAuditCustomerUseCase:
    """Заказчик и реквизиты."""

    def __init__(
        self,
        *,
        access: AuditAccess,
        customers: AuditCustomerRepository,
        users: UserRepository,
    ) -> None:
        """Доступ, реквизиты и аккаунты."""

        self.access = access
        self.customers = customers
        self.users = users

    async def execute(
        self,
        *,
        audit_id: int,
        user: User,
    ) -> AuditCustomerResponse:
        """Получить заказчика аудита."""

        audit = await self.access.get_visible(
            audit_id=audit_id,
            user=user,
        )
        customer = await self.users.get_by_id(user_id=audit.customer_id)
        if customer is None:
            raise UserNotFoundError()

        company = await self.customers.get_company(audit_id=audit_id)
        company_response = None
        if company is not None:
            company_response = AuditCompanyResponse.from_model(company=company)

        return AuditCustomerResponse(
            id=customer.id,
            full_name=customer.full_name,
            customer_type=audit.customer_type,
            company=company_response,
        )
