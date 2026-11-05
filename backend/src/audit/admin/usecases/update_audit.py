"""Изменение аудита администратором."""

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.admin.schemas.audit import UpdateAuditRequest
from src.audit.audit_letters import AuditLetters
from src.audit.enums import AuditStatus
from src.audit.exceptions import AuditNotFoundError, InvalidAuditApplicationError
from src.audit.repositories.audit_applications import AuditApplicationRepository
from src.audit.repositories.audits import AuditRepository
from src.notifications.models.notification import Notification
from src.notifications.options import NOTIFICATION_TEXT_MAX_LENGTH
from src.notifications.repositories.notifications import NotificationRepository
from src.users.enums import UserRole
from src.users.repositories.expert_profiles import ExpertProfileRepository
from src.users.repositories.users import UserRepository


class UpdateAuditUseCase:
    """Изменение этапа, цены и руководителя."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        audits: AuditRepository,
        applications: AuditApplicationRepository,
        users: UserRepository,
        profiles: ExpertProfileRepository,
        notifications: NotificationRepository,
        letters: AuditLetters,
    ) -> None:
        """Аудиты, руководители и уведомления."""

        self.session = session
        self.audits = audits
        self.applications = applications
        self.users = users
        self.profiles = profiles
        self.notifications = notifications
        self.letters = letters

    async def execute(
        self,
        *,
        audit_id: int,
        payload: UpdateAuditRequest,
    ) -> None:
        """Сохранить изменения администратора."""

        audit = await self.audits.get_for_update(audit_id=audit_id)
        if audit is None:
            raise AuditNotFoundError()

        if payload.lead_id is not None:
            lead = await self.users.get_by_id(user_id=payload.lead_id)
            profile = await self.profiles.get_by_user_id(user_id=payload.lead_id)
            if (
                lead is None
                or lead.role != UserRole.EXPERT
                or profile is None
                or not profile.audit_lead
            ):
                raise InvalidAuditApplicationError("Выберите руководителя аудиторской группы")

        if (
            payload.status not in (AuditStatus.NEW, AuditStatus.CONSULTATION)
            and payload.lead_id is None
        ):
            raise InvalidAuditApplicationError("Для этого статуса нужен руководитель группы")

        consultation_is_completed = (
            audit.status == AuditStatus.CONSULTATION
            and payload.status == AuditStatus.NEW
            and payload.lead_id is None
        )
        if payload.lead_id is not None and audit.lead_ready_at is None:
            audit.lead_ready_at = datetime.now(UTC)

        audit.lead_id = payload.lead_id
        audit.status = payload.status
        audit.agreed_price = payload.price
        if payload.status in (AuditStatus.NEW, AuditStatus.CONSULTATION):
            audit.customer_budget = payload.price
            audit.agreed_price = None

        recipients = []
        object_name = "Аудит СУПБ"
        if consultation_is_completed:
            recipients = await self.profiles.list_audit_leads()
            application = await self.applications.get(audit_id=audit_id)
            if application is not None and application.object_name:
                object_name = application.object_name

            await self.notifications.add_many(
                notifications=[
                    Notification(
                        user_id=lead.id,
                        audit_id=audit_id,
                        text=f"Новая заявка на аудит СУПБ: {object_name}"[
                            :NOTIFICATION_TEXT_MAX_LENGTH
                        ],
                    )
                    for lead in recipients
                ]
            )

        await self.audits.save(audit=audit)
        await self.session.commit()

        if recipients:
            await self.letters.send_new_application(
                audit_id=audit_id,
                object_name=object_name,
                recipients=[lead.email for lead in recipients],
            )
