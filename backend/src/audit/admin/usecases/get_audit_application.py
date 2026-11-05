"""Просмотр анкеты аудита."""

from src.audit.exceptions import AuditNotFoundError
from src.audit.repositories.audit_applications import AuditApplicationRepository
from src.audit.repositories.audits import AuditRepository
from src.audit.schemas.audit_application import AuditApplicationResponse
from src.audit.schemas.audit_details import AuditDetailsSchema


class GetAdminAuditApplicationUseCase:
    """Анкета заказчика."""

    def __init__(
        self,
        *,
        audits: AuditRepository,
        applications: AuditApplicationRepository,
    ) -> None:
        """Заявки и анкеты."""

        self.audits = audits
        self.applications = applications

    async def execute(self, *, audit_id: int) -> AuditApplicationResponse | None:
        """Получить анкету аудита."""

        audit = await self.audits.get_by_id(audit_id=audit_id)

        if audit is None:
            raise AuditNotFoundError()

        application = await self.applications.get(audit_id=audit_id)
        if application is None:
            return None

        details = None
        if application.details is not None:
            details = AuditDetailsSchema.model_validate(application.details)

        return AuditApplicationResponse(
            object_name=application.object_name,
            details=details,
        )
