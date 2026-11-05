"""Просмотр плана аудита."""

from src.audit.repositories.audit_plans import AuditPlanRepository
from src.audit.site.audit_access import AuditAccess
from src.audit.site.schemas.audit_plan import AuditPlanResponse, AuditPlanReviewResponse
from src.users.models.user import User


class GetAuditPlanUseCase:
    """План и состояние его согласования."""

    def __init__(
        self,
        *,
        access: AuditAccess,
        plans: AuditPlanRepository,
    ) -> None:
        """Доступ и планы."""

        self.access = access
        self.plans = plans

    async def execute(
        self,
        *,
        audit_id: int,
        user: User,
    ) -> AuditPlanReviewResponse | None:
        """Получить план аудита."""

        await self.access.get_visible(
            audit_id=audit_id,
            user=user,
        )
        plan = await self.plans.get(audit_id=audit_id)
        if plan is None:
            return None

        schedule = None
        if plan.plan is not None:
            schedule = AuditPlanResponse.model_validate(plan.plan)

        return AuditPlanReviewResponse(
            schedule=schedule,
            comment=plan.comment,
            sent_at=plan.sent_at,
            approved_at=plan.approved_at,
        )
