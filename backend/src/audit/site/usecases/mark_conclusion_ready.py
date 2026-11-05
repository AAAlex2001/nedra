"""Сообщить о готовности заключения."""

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


class MarkAuditConclusionReadyUseCase:
    """Сообщить о готовности заключения."""

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
        """Сообщить о готовности заключения."""

        audit = await self.audits.get_for_update(audit_id=audit_id)

        if audit is None or audit.lead_id != user.id or user.role != UserRole.EXPERT:
            raise AuditNotFoundError()

        if audit.status != AuditStatus.IN_PROGRESS:
            raise AuditStateError("Действие недоступно на этом этапе")

        notification = Notification(
            user_id=audit.customer_id,
            audit_id=audit_id,
            text=f"Заключение готово к выдаче, №{audit_id}",
        )

        audit.status = AuditStatus.CONCLUSION_READY
        audit.conclusion_ready_at = datetime.now(UTC)
        await self.audits.save(audit=audit)
        await self.notifications.add(notification=notification)
        response = AuditResponse.from_model(audit=audit)

        await self.session.commit()
        await self.email_delivery.send(notification=notification)

        return response
