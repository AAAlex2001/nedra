"""Ответ аудитора на встречную цену."""

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.audit_letters import AuditLetters
from src.audit.enums import AuditStatus
from src.audit.exceptions import AuditNotFoundError, AuditStateError
from src.audit.repositories.audits import AuditRepository
from src.audit.site.schemas.answer_audit_counter_offer import (
    AnswerAuditCounterOfferResponse,
)
from src.notifications.models.notification import Notification
from src.notifications.repositories.notifications import NotificationRepository
from src.users.enums import UserRole
from src.users.exceptions import UserNotFoundError
from src.users.models.user import User
from src.users.repositories.users import UserRepository


class AnswerAuditCounterOfferUseCase:
    """Согласование встречной цены аудитором."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        audits: AuditRepository,
        users: UserRepository,
        notifications: NotificationRepository,
        letters: AuditLetters,
    ) -> None:
        """Аудиты, участники и уведомления."""

        self.session = session
        self.audits = audits
        self.users = users
        self.notifications = notifications
        self.letters = letters

    async def execute(
        self,
        *,
        user: User,
        audit_id: int,
        accept: bool,
    ) -> AnswerAuditCounterOfferResponse:
        """Ответить на встречную стоимость."""

        audit = await self.audits.get_for_update(audit_id=audit_id)

        if audit is None or audit.lead_id != user.id or user.role != UserRole.EXPERT:
            raise AuditNotFoundError()

        if audit.status != AuditStatus.COUNTER or audit.counter_price is None:
            raise AuditStateError("Нет встречного предложения")

        customer = await self.users.get_by_id(user_id=audit.customer_id)

        if customer is None:
            raise UserNotFoundError()

        if accept:
            audit.agreed_price = audit.counter_price
            audit.lead_ready_at = datetime.now(UTC)
            audit.status = AuditStatus.EXPERT_READY
            notification_text = "Руководитель аудита принял предложенную вами стоимость"
        else:
            audit.lead_id = None
            audit.agreed_price = None
            audit.lead_ready_at = None
            audit.status = AuditStatus.NEW
            notification_text = (
                "Руководитель аудита отклонил вашу цену. Заявка снова доступна другим аудиторам"
            )

        audit.offer_price = None
        audit.counter_price = None
        await self.audits.save(audit=audit)
        await self.notifications.add(
            notification=Notification(
                user_id=customer.id,
                audit_id=audit_id,
                text=notification_text,
            )
        )
        response = AnswerAuditCounterOfferResponse.from_model(audit=audit)
        await self.session.commit()
        await self.letters.send_price_update(
            audit_id=audit_id,
            recipient=customer.email,
            text=notification_text,
        )

        return response
