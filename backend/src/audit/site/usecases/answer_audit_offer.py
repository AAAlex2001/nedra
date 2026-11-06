"""Ответ заказчика на предложение аудитора."""

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.audit_letters import AuditLetters
from src.audit.audit_price import format_audit_price, validate_audit_price
from src.audit.enums import AuditOfferAnswer, AuditStatus
from src.audit.exceptions import (
    AuditNotFoundError,
    AuditStateError,
    InvalidAuditPriceError,
)
from src.audit.repositories.audits import AuditRepository
from src.audit.site.schemas.answer_audit_offer import AnswerAuditOfferResponse
from src.notifications.models.notification import Notification
from src.notifications.repositories.notifications import NotificationRepository
from src.users.enums import UserRole
from src.users.exceptions import UserNotFoundError
from src.users.models.user import User
from src.users.repositories.users import UserRepository


class AnswerAuditOfferUseCase:
    """Согласование цены заказчиком."""

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
        answer: AuditOfferAnswer,
        price: Decimal | None = None,
    ) -> AnswerAuditOfferResponse:
        """Ответить на стоимость аудита."""

        audit = await self.audits.get_for_update(audit_id=audit_id)

        if audit is None or audit.customer_id != user.id or user.role != UserRole.CUSTOMER:
            raise AuditNotFoundError()

        if audit.status != AuditStatus.OFFER or audit.offer_price is None or audit.lead_id is None:
            raise AuditStateError("Нет предложения, на которое можно ответить")

        lead = await self.users.get_by_id(user_id=audit.lead_id)

        if lead is None:
            raise UserNotFoundError()

        if answer == AuditOfferAnswer.ACCEPT:
            audit.agreed_price = audit.offer_price
            audit.offer_price = None
            audit.counter_price = None
            audit.lead_ready_at = datetime.now(UTC)
            audit.status = AuditStatus.EXPERT_READY
            notification_text = "Заказчик принял предложенную стоимость аудита"
        elif answer == AuditOfferAnswer.COUNTER:
            if not audit.negotiation_allowed:
                raise AuditStateError("Обсуждение стоимости не предусмотрено")

            if price is None:
                raise InvalidAuditPriceError("Укажите свою цену")

            validate_audit_price(price=price)

            if price >= audit.offer_price:
                raise InvalidAuditPriceError("Встречная цена должна быть ниже предложения аудитора")

            audit.counter_price = price
            audit.status = AuditStatus.COUNTER
            notification_text = (
                f"Заказчик предлагает провести аудит за {format_audit_price(price=price)} ₽"
            )
        elif answer == AuditOfferAnswer.DECLINE:
            audit.lead_id = None
            audit.offer_price = None
            audit.counter_price = None
            audit.agreed_price = None
            audit.lead_ready_at = None
            audit.status = AuditStatus.NEW
            notification_text = "Заказчик отказался от предложенной стоимости аудита"
        else:
            raise AuditStateError("Неизвестный ответ на предложение")

        await self.audits.save(audit=audit)
        await self.notifications.add(
            notification=Notification(
                user_id=lead.id,
                audit_id=audit_id,
                text=notification_text,
            )
        )
        response = AnswerAuditOfferResponse.from_model(audit=audit)
        await self.session.commit()
        await self.letters.send_price_update(
            audit_id=audit_id,
            recipient=lead.email,
            text=notification_text,
        )

        return response
