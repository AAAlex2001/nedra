"""Замечания заказчика к плану аудита."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.audit_letters import AuditLetters
from src.audit.enums import AuditStatus
from src.audit.exceptions import AuditNotFoundError, AuditStateError
from src.audit.repositories.audit_plans import AuditPlanRepository
from src.audit.repositories.audits import AuditRepository
from src.audit.site.schemas.request_audit_plan_changes import (
    RequestAuditPlanChangesResponse,
)
from src.notifications.models.notification import Notification
from src.notifications.repositories.notifications import NotificationRepository
from src.users.enums import UserRole
from src.users.exceptions import UserNotFoundError
from src.users.models.user import User
from src.users.repositories.users import UserRepository


class RequestAuditPlanChangesUseCase:
    """Возврат плана на доработку."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        audits: AuditRepository,
        plans: AuditPlanRepository,
        users: UserRepository,
        notifications: NotificationRepository,
        letters: AuditLetters,
    ) -> None:
        """Планы, участники и уведомления."""

        self.session = session
        self.audits = audits
        self.plans = plans
        self.users = users
        self.notifications = notifications
        self.letters = letters

    async def execute(
        self,
        *,
        user: User,
        audit_id: int,
        comment: str,
    ) -> RequestAuditPlanChangesResponse:
        """Запросить изменения плана."""

        audit = await self.audits.get_for_update(audit_id=audit_id)

        if audit is None or audit.customer_id != user.id or user.role != UserRole.CUSTOMER:
            raise AuditNotFoundError()

        plan = await self.plans.get(audit_id=audit_id)

        if audit.status != AuditStatus.PLAN_REVIEW or audit.lead_id is None or plan is None:
            raise AuditStateError("План аудита сейчас не ждёт согласования")

        lead = await self.users.get_by_id(user_id=audit.lead_id)

        if lead is None:
            raise UserNotFoundError()

        plan.comment = comment.strip()
        audit.status = AuditStatus.PLAN
        await self.plans.save(plan=plan)
        await self.notifications.add(
            notification=Notification(
                user_id=lead.id,
                audit_id=audit_id,
                text=f"Заказчик просит скорректировать план аудита по заявке №{audit_id}",
            )
        )
        response = RequestAuditPlanChangesResponse.from_model(audit=audit)
        await self.session.commit()
        await self.letters.send_plan_changes(
            audit_id=audit_id,
            recipient=lead.email,
            comment=plan.comment,
        )

        return response
