"""Списки аудитов в кабинете."""

from typing import Literal

from src.audit.exceptions import AuditAccessError
from src.audit.repositories.audits import AuditRepository
from src.audit.site.schemas.list_audits import AuditListItemResponse
from src.users.enums import UserRole
from src.users.models.user import User
from src.users.repositories.expert_profiles import ExpertProfileRepository


class ListAuditsUseCase:
    """Свои, назначенные и доступные работы."""

    def __init__(
        self,
        *,
        audits: AuditRepository,
        profiles: ExpertProfileRepository,
    ) -> None:
        """Работы пользователя."""

        self.audits = audits
        self.profiles = profiles

    async def execute(
        self,
        *,
        user: User,
        scope: Literal["my", "assigned", "incoming"],
    ) -> list[AuditListItemResponse]:
        """Получить выбранный список работ."""

        if scope == "my":
            if user.role != UserRole.CUSTOMER:
                raise AuditAccessError("Этот список доступен заказчику")

            audits = await self.audits.list_for_customer(user_id=user.id)
        else:
            if user.role != UserRole.EXPERT:
                raise AuditAccessError("Этот список доступен эксперту")

            if scope == "assigned":
                audits = await self.audits.list_assigned(user_id=user.id)
            else:
                profile = await self.profiles.get_by_user_id(user_id=user.id)

                if profile is None or not profile.audit_lead:
                    return []

                audits = await self.audits.list_incoming()

        return [AuditListItemResponse.from_model(audit=audit) for audit in audits]
