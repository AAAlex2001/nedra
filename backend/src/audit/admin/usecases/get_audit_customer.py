"""Просмотр заказчика аудита."""

from src.audit.exceptions import AuditNotFoundError
from src.audit.repositories.audit_customers import AuditCustomerRepository
from src.audit.repositories.audits import AuditRepository
from src.audit.schemas.audit_company import AuditCompanyResponse
from src.audit.schemas.audit_participants import AuditCustomerResponse
from src.users.exceptions import UserNotFoundError
from src.users.repositories.users import UserRepository


class GetAdminAuditCustomerUseCase:
    """Заказчик и реквизиты."""

    def __init__(
        self,
        *,
        audits: AuditRepository,
        customers: AuditCustomerRepository,
        users: UserRepository,
    ) -> None:
        """Заявки, реквизиты и аккаунты."""

        self.audits = audits
        self.customers = customers
        self.users = users

    async def execute(self, *, audit_id: int) -> AuditCustomerResponse:
        """Получить заказчика аудита."""

        audit = await self.audits.get_by_id(audit_id=audit_id)

        if audit is None:
            raise AuditNotFoundError()

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
