"""Доступ к аудиту."""

from src.audit.enums import AuditStatus
from src.audit.exceptions import AuditNotFoundError
from src.audit.models.audit import Audit
from src.audit.repositories.audit_teams import AuditTeamRepository
from src.audit.repositories.audits import AuditRepository
from src.users.enums import UserRole
from src.users.models.user import User
from src.users.repositories.expert_profiles import ExpertProfileRepository


class AuditAccess:
    """Проверка участника и квалификации."""

    def __init__(
        self,
        *,
        audits: AuditRepository,
        teams: AuditTeamRepository,
        profiles: ExpertProfileRepository,
    ) -> None:
        """Услуга и права участника."""

        self.audits = audits
        self.teams = teams
        self.profiles = profiles

    async def get_visible(
        self,
        *,
        audit_id: int,
        user: User,
    ) -> Audit:
        """Найти доступную пользователю услугу."""

        audit = await self.audits.get_by_id(audit_id=audit_id)

        if audit is None:
            raise AuditNotFoundError()

        if user.role == UserRole.CUSTOMER and audit.customer_id == user.id:
            return audit

        if user.role != UserRole.EXPERT:
            raise AuditNotFoundError()

        if audit.lead_id == user.id:
            return audit

        member_ids = await self.teams.list_user_ids(audit_id=audit_id)

        if user.id in member_ids:
            return audit

        if audit.status == AuditStatus.NEW and audit.lead_id is None:
            profile = await self.profiles.get_by_user_id(user_id=user.id)

            if profile is not None and profile.audit_lead:
                return audit

        raise AuditNotFoundError()
