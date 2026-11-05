"""Предложение стоимости аудита."""

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.audit_letters import AuditLetters
from src.audit.audit_price import format_audit_price, validate_audit_price
from src.audit.enums import AuditStatus
from src.audit.exceptions import AuditAccessError, AuditNotFoundError, AuditStateError
from src.audit.repositories.audits import AuditRepository
from src.audit.schemas.audit import AuditResponse
from src.notifications.models.notification import Notification
from src.notifications.repositories.notifications import NotificationRepository
from src.users.enums import UserRole
from src.users.exceptions import UserNotFoundError
from src.users.models.user import User
from src.users.repositories.expert_profiles import ExpertProfileRepository
from src.users.repositories.users import UserRepository


class ProposeAuditPriceUseCase:
    """Предложение цены руководителем аудита."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        audits: AuditRepository,
        profiles: ExpertProfileRepository,
        users: UserRepository,
        notifications: NotificationRepository,
        letters: AuditLetters,
    ) -> None:
        """Аудиты, участники и уведомления."""

        self.session = session
        self.audits = audits
        self.profiles = profiles
        self.users = users
        self.notifications = notifications
        self.letters = letters

    async def execute(
        self,
        *,
        user: User,
        audit_id: int,
        price: Decimal,
    ) -> AuditResponse:
        """Предложить стоимость аудита."""

        validate_audit_price(price=price)

        if user.role != UserRole.EXPERT:
            raise AuditAccessError("Предлагать цену может руководитель аудита")

        profile = await self.profiles.get_by_user_id(user_id=user.id)

        if profile is None or not profile.audit_lead:
            raise AuditAccessError("Нет права руководить аудиторской группой")

        audit = await self.audits.get_for_update(audit_id=audit_id)

        if audit is None or audit.lead_id not in (None, user.id):
            raise AuditNotFoundError()

        if audit.status != AuditStatus.NEW or audit.lead_id is not None:
            raise AuditStateError("Предложение уже отправлено")

        if audit.customer_budget is not None and not audit.negotiation_allowed:
            raise AuditStateError("Заказчик указал фиксированный бюджет")

        customer = await self.users.get_by_id(user_id=audit.customer_id)

        if customer is None:
            raise UserNotFoundError()

        audit.lead_id = user.id
        audit.offer_price = price
        audit.counter_price = None
        audit.status = AuditStatus.OFFER
        await self.audits.save(audit=audit)

        notification_text = (
            f"Руководитель группы предлагает провести аудит за {format_audit_price(price=price)} ₽"
        )
        await self.notifications.add(
            notification=Notification(
                user_id=customer.id,
                audit_id=audit_id,
                text=notification_text,
            )
        )
        response = AuditResponse.from_model(audit=audit)
        await self.session.commit()
        await self.letters.send_price_update(
            audit_id=audit_id,
            recipient=customer.email,
            text=notification_text,
        )

        return response
