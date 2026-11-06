"""Просмотр группы аудиторов."""

from src.audit.repositories.audit_plans import AuditPlanRepository
from src.audit.site.audit_access import AuditAccess
from src.audit.site.audit_team_members import AuditTeamMembers
from src.audit.site.schemas.audit_team import AuditTeamMemberResponse
from src.users.enums import UserRole
from src.users.models.user import User


class GetAuditTeamUseCase:
    """Состав группы, доступный участнику."""

    def __init__(
        self,
        *,
        access: AuditAccess,
        plans: AuditPlanRepository,
        members: AuditTeamMembers,
    ) -> None:
        """Доступ, согласование плана и группа."""

        self.access = access
        self.plans = plans
        self.members = members

    async def execute(
        self,
        *,
        audit_id: int,
        user: User,
    ) -> list[AuditTeamMemberResponse]:
        """Получить группу аудиторов."""

        audit = await self.access.get_visible(
            audit_id=audit_id,
            user=user,
        )
        if user.role == UserRole.CUSTOMER:
            plan = await self.plans.get(audit_id=audit_id)
            if plan is None or plan.sent_at is None:
                return []

        return await self.members.list_for_audit(audit=audit)
