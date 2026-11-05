"""Отправка плана аудита заказчику."""

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.audit_letters import AuditLetters
from src.audit.enums import AuditStatus
from src.audit.exceptions import AuditNotFoundError, AuditStateError, InvalidAuditApplicationError
from src.audit.models.audit_document import AuditDocument
from src.audit.models.audit_plan import AuditPlan
from src.audit.repositories.audit_plans import AuditPlanRepository
from src.audit.repositories.audits import AuditRepository
from src.audit.schemas.audit import AuditResponse
from src.audit.site.audit_plan_files import AuditPlanFiles
from src.audit.site.audit_plan_preparation import AuditPlanPreparation
from src.audit.site.schemas.audit_plan import AuditPlanResponse, SubmitAuditPlanRequest
from src.notifications.models.notification import Notification
from src.notifications.repositories.notifications import NotificationRepository
from src.users.enums import UserRole
from src.users.exceptions import UserNotFoundError
from src.users.models.user import User
from src.users.repositories.users import UserRepository


class SubmitAuditPlanUseCase:
    """Новая версия программы аудита."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        audits: AuditRepository,
        plans: AuditPlanRepository,
        users: UserRepository,
        notifications: NotificationRepository,
        files: AuditPlanFiles,
        preparation: AuditPlanPreparation,
        letters: AuditLetters,
    ) -> None:
        """Планы, участники, файлы и уведомления."""

        self.session = session
        self.audits = audits
        self.plans = plans
        self.users = users
        self.notifications = notifications
        self.files = files
        self.preparation = preparation
        self.letters = letters

    async def execute(
        self,
        *,
        user: User,
        audit_id: int,
        payload: SubmitAuditPlanRequest,
    ) -> AuditResponse:
        """Отправить план на согласование."""

        audit = await self.audits.get_for_update(audit_id=audit_id)

        if audit is None or audit.lead_id != user.id or user.role != UserRole.EXPERT:
            raise AuditNotFoundError()

        if audit.status != AuditStatus.PLAN:
            raise AuditStateError("Сейчас план аудита не ожидается")

        document_data = await self.preparation.get_data(audit=audit)

        if "onsite" in document_data.details.stages and payload.onsite_start is None:
            raise InvalidAuditApplicationError("Заказчик выбрал выездной этап: укажите его даты")

        customer = await self.users.get_by_id(user_id=audit.customer_id)

        if customer is None:
            raise UserNotFoundError()

        plan = await self.plans.get(audit_id=audit_id)
        version = 1
        if plan is not None and plan.plan is not None:
            previous_plan = AuditPlanResponse.model_validate(plan.plan)
            version = previous_plan.version + 1
        plan_data = AuditPlanResponse.from_request(
            payload=payload,
            version=version,
        )
        submitted_at = datetime.now(UTC)
        document = await self.files.save(
            plan_details=document_data,
            plan=plan_data,
            generated_at=submitted_at,
        )

        try:
            if plan is None:
                plan = AuditPlan(audit_id=audit_id)

            plan.plan = plan_data.model_dump(mode="json")
            plan.comment = None
            plan.sent_at = submitted_at
            plan.approved_at = None
            audit.status = AuditStatus.PLAN_REVIEW

            await self.plans.save_with_document(
                plan=plan,
                document=AuditDocument(
                    audit_id=audit_id,
                    uploaded_by=user.id,
                    kind="audit_plan",
                    file_path=document.path,
                    original_name=document.original_name,
                    size=document.size,
                    content_type=document.content_type,
                ),
            )
            await self.notifications.add(
                notification=Notification(
                    user_id=audit.customer_id,
                    audit_id=audit_id,
                    text=f"План аудита по заявке №{audit_id} ждёт вашего согласования",
                )
            )
            response = AuditResponse.from_model(audit=audit)
        except Exception:
            try:
                await self.session.rollback()
            finally:
                await self.files.remove_failed(document=document)

            raise

        await self.session.commit()
        await self.letters.send_plan_submitted(
            audit_id=audit_id,
            recipient=customer.email,
        )

        return response
