"""Принять выполненную работу."""

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.enums import AuditStatus
from src.audit.exceptions import AuditNotFoundError, AuditStateError
from src.audit.repositories.audits import AuditRepository
from src.audit.schemas.audit import AuditResponse
from src.notifications.email_delivery import NotificationEmailDelivery
from src.notifications.models.notification import Notification
from src.notifications.repositories.notifications import NotificationRepository
from src.users.enums import UserRole
from src.users.models.user import User


class AcceptAuditWorkUseCase:
    """Принять выполненную работу."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        audits: AuditRepository,
        notifications: NotificationRepository,
        email_delivery: NotificationEmailDelivery,
    ) -> None:
        """Хранение и уведомления."""

        self.session = session
        self.audits = audits
        self.notifications = notifications
        self.email_delivery = email_delivery

    async def execute(
        self,
        *,
        audit_id: int,
        user: User,
    ) -> AuditResponse:
        """Принять выполненную работу."""

        audit = await self.audits.get_for_update(audit_id=audit_id)

        if audit is None or audit.customer_id != user.id or user.role != UserRole.CUSTOMER:
            raise AuditNotFoundError()

        if audit.status != AuditStatus.SENT:
            raise AuditStateError("Действие недоступно на этом этапе")

        if audit.lead_id is None:
            raise AuditStateError("Исполнитель не назначен")

        notification = Notification(
            user_id=audit.lead_id,
            audit_id=audit_id,
            text=f"Заказчик принял работу, №{audit_id}",
        )

        audit.status = AuditStatus.ACCEPTED
        audit.accepted_at = datetime.now(UTC)
        await self.audits.save(audit=audit)
        await self.notifications.add(notification=notification)
        response = AuditResponse.from_model(audit=audit)

        await self.session.commit()
        await self.email_delivery.send(notification=notification)

        return response
