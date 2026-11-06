"""Просмотр заявок администратором."""

from src.audit.admin.schemas.audit import AuditAdminResponse
from src.audit.repositories.audit_applications import AuditApplicationRepository
from src.audit.repositories.audits import AuditRepository
from src.users.exceptions import UserNotFoundError
from src.users.repositories.users import UserRepository


class ListAdminAuditsUseCase:
    """Список работ с именами участников."""

    def __init__(
        self,
        *,
        audits: AuditRepository,
        users: UserRepository,
        applications: AuditApplicationRepository,
    ) -> None:
        """Работы и участники."""

        self.audits = audits
        self.users = users
        self.applications = applications

    async def execute(self) -> list[AuditAdminResponse]:
        """Получить все работы."""

        audits = await self.audits.list_all()
        user_ids = {record.customer_id for record in audits}
        user_ids.update(record.lead_id for record in audits if record.lead_id is not None)
        users = await self.users.list_by_ids(user_ids=user_ids)
        applications = await self.applications.list_by_audit_ids(
            audit_ids={audit.id for audit in audits}
        )
        response = []

        for audit in audits:
            customer = users.get(audit.customer_id)
            if customer is None:
                raise UserNotFoundError()

            lead = users.get(audit.lead_id)
            response.append(
                AuditAdminResponse(
                    id=audit.id,
                    status=audit.status,
                    customer_id=customer.id,
                    customer_name=customer.full_name,
                    lead_id=audit.lead_id,
                    lead_name=lead.full_name if lead is not None else None,
                    object_name=applications[audit.id].object_name
                    if audit.id in applications
                    else None,
                    price=audit.agreed_price
                    if audit.agreed_price is not None
                    else audit.customer_budget,
                    created_at=audit.created_at,
                ),
            )

        return response
