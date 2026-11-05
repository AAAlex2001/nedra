"""Подготовка данных программы аудита."""

from src.audit.exceptions import InvalidAuditApplicationError
from src.audit.models.audit import Audit
from src.audit.repositories.audit_applications import AuditApplicationRepository
from src.audit.repositories.audit_customers import AuditCustomerRepository
from src.audit.schemas.audit_details import AuditDetailsSchema
from src.audit.site.audit_plan_data import AuditPlanData
from src.audit.site.audit_team_members import AuditTeamMembers


class AuditPlanPreparation:
    """Данные для печатной программы."""

    def __init__(
        self,
        *,
        applications: AuditApplicationRepository,
        customers: AuditCustomerRepository,
        members: AuditTeamMembers,
    ) -> None:
        """Анкеты, реквизиты и состав группы."""

        self.applications = applications
        self.customers = customers
        self.members = members

    async def get_data(self, *, audit: Audit) -> AuditPlanData:
        """Получить данные для документа."""

        application = await self.applications.get(audit_id=audit.id)
        if application is None or application.details is None:
            raise InvalidAuditApplicationError("В заявке нет анкеты аудита")

        company = await self.customers.get_company(audit_id=audit.id)
        team = await self.members.list_for_audit(audit=audit)
        details = AuditDetailsSchema.model_validate(application.details)

        return AuditPlanData(
            audit_id=audit.id,
            details=details,
            company=company,
            team=team,
        )
