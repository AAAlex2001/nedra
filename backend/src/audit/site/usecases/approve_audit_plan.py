"""Согласование плана заказчиком."""

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.audit_letters import AuditLetters
from src.audit.enums import AuditStatus
from src.audit.exceptions import AuditNotFoundError, AuditStateError
from src.audit.repositories.audit_applications import AuditApplicationRepository
from src.audit.repositories.audit_plans import AuditPlanRepository
from src.audit.repositories.audit_teams import AuditTeamRepository
from src.audit.repositories.audits import AuditRepository
from src.audit.schemas.audit import AuditResponse
from src.audit.site.schemas.audit_plan import AuditPlanResponse
from src.notifications.models.notification import Notification
from src.notifications.repositories.notifications import NotificationRepository
from src.users.enums import UserRole
from src.users.models.user import User
from src.users.repositories.users import UserRepository


class ApproveAuditPlanUseCase:
    """Переход к проверке документов."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        audits: AuditRepository,
        plans: AuditPlanRepository,
        applications: AuditApplicationRepository,
        teams: AuditTeamRepository,
        users: UserRepository,
        notifications: NotificationRepository,
        letters: AuditLetters,
    ) -> None:
        """Планы, группа и уведомления."""

        self.session = session
        self.audits = audits
        self.plans = plans
        self.applications = applications
        self.teams = teams
        self.users = users
        self.notifications = notifications
        self.letters = letters

    async def execute(
        self,
        *,
        user: User,
        audit_id: int,
    ) -> AuditResponse:
        """Согласовать план аудита."""

        audit = await self.audits.get_for_update(audit_id=audit_id)

        if audit is None or audit.customer_id != user.id or user.role != UserRole.CUSTOMER:
            raise AuditNotFoundError()

        plan = await self.plans.get(audit_id=audit_id)

        if (
            audit.status != AuditStatus.PLAN_REVIEW
            or plan is None
            or plan.plan is None
            or audit.lead_id is None
        ):
            raise AuditStateError("План аудита сейчас не ждёт согласования")

        member_ids = set(await self.teams.list_user_ids(audit_id=audit_id))
        member_ids.add(audit.lead_id)
        participants = await self.users.list_by_ids(user_ids=member_ids | {user.id})

        application = await self.applications.get(audit_id=audit_id)
        schedule = AuditPlanResponse.model_validate(plan.plan)

        plan.approved_at = datetime.now(UTC)
        audit.status = AuditStatus.IN_PROGRESS
        await self.plans.save(plan=plan)
        notifications = [
            Notification(
                user_id=member_id,
                audit_id=audit_id,
                text=f"Заказчик согласовал план аудита по заявке №{audit_id}, документы открыты для проверки",
            )
            for member_id in sorted(member_ids)
        ]
        await self.notifications.add_many(notifications=notifications)
        response = AuditResponse.from_model(audit=audit)
        await self.session.commit()
        await self.letters.send_plan_approved(
            audit_id=audit_id,
            object_name=application.object_name if application is not None else None,
            plan=schedule,
            recipients=[participant.email for participant in participants.values()],
        )

        return response
