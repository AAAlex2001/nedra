"""Просмотр анкеты аудита."""

from src.audit.repositories.audit_applications import AuditApplicationRepository
from src.audit.schemas.audit_application import AuditApplicationResponse
from src.audit.schemas.audit_details import AuditDetailsSchema
from src.audit.site.audit_access import AuditAccess
from src.users.models.user import User


class GetAuditApplicationUseCase:
    """Анкета заказчика."""

    def __init__(
        self,
        *,
        access: AuditAccess,
        applications: AuditApplicationRepository,
    ) -> None:
        """Доступ и анкеты."""

        self.access = access
        self.applications = applications

    async def execute(
        self,
        *,
        audit_id: int,
        user: User,
    ) -> AuditApplicationResponse | None:
        """Получить анкету аудита."""

        await self.access.get_visible(
            audit_id=audit_id,
            user=user,
        )
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
