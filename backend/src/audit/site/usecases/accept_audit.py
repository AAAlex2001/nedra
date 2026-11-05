"""Принятие аудита исполнителем."""

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.audit_letters import AuditLetters
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


class AcceptAuditUseCase:
    """Согласие с условиями заказчика."""

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
        """Услуга, участники и уведомления."""

        self.session = session
        self.audits = audits
        self.profiles = profiles
        self.users = users
        self.notifications = notifications
        self.letters = letters

    async def execute(
        self,
        *,
        audit_id: int,
        user: User,
    ) -> AuditResponse:
        """Принять работу на условиях заказчика."""

        if user.role != UserRole.EXPERT:
            raise AuditAccessError("Работу принимает эксперт")

        audit = await self.audits.get_for_update(audit_id=audit_id)

        if audit is None:
            raise AuditNotFoundError()

        if audit.status != AuditStatus.NEW or audit.lead_id is not None:
            raise AuditStateError("Заявку уже взял другой исполнитель")

        profile = await self.profiles.get_by_user_id(user_id=user.id)

        if profile is None or not profile.audit_lead:
            raise AuditAccessError("Нет права руководить аудиторской группой")

        if audit.customer_budget is None:
            raise AuditStateError("В заявке нет цены: предложите свою")

        audit.lead_id = user.id
        audit.agreed_price = audit.customer_budget
        audit.lead_ready_at = datetime.now(UTC)

        customer = await self.users.get_by_id(user_id=audit.customer_id)

        if customer is None:
            raise UserNotFoundError()

        audit.status = AuditStatus.EXPERT_READY
        await self.audits.save(audit=audit)
        await self.notifications.add(
            notification=Notification(
                user_id=customer.id,
                audit_id=audit_id,
                text=f"Исполнитель готов выполнить аудит №{audit_id}",
            )
        )
        response = AuditResponse.from_model(audit=audit)
        await self.session.commit()
        await self.letters.send_price_update(
            audit_id=audit_id,
            recipient=customer.email,
            text="Руководитель группы принял аудит на ваших условиях",
        )

        return response
