"""Изменение состава аудиторской группы."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.enums import AuditStatus
from src.audit.exceptions import AuditNotFoundError, AuditStateError, InvalidAuditApplicationError
from src.audit.repositories.audit_teams import AuditTeamRepository
from src.audit.repositories.audits import AuditRepository
from src.audit.schemas.audit import AuditResponse
from src.notifications.models.notification import Notification
from src.notifications.repositories.notifications import NotificationRepository
from src.users.enums import UserRole
from src.users.models.user import User
from src.users.options import AUDIT_DIRECTION
from src.users.repositories.expert_profiles import ExpertProfileRepository


class SetAuditTeamUseCase:
    """Назначение участников руководителем группы."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        audits: AuditRepository,
        teams: AuditTeamRepository,
        profiles: ExpertProfileRepository,
        notifications: NotificationRepository,
    ) -> None:
        """Аудиты, группы и уведомления."""

        self.session = session
        self.audits = audits
        self.teams = teams
        self.profiles = profiles
        self.notifications = notifications

    async def execute(
        self,
        *,
        user: User,
        audit_id: int,
        user_ids: list[int],
    ) -> AuditResponse:
        """Изменить состав группы."""

        audit = await self.audits.get_for_update(audit_id=audit_id)

        if audit is None or audit.lead_id != user.id or user.role != UserRole.EXPERT:
            raise AuditNotFoundError()

        if audit.status not in (AuditStatus.CONTRACT, AuditStatus.PLAN):
            raise AuditStateError("Состав группы меняется до отправки плана аудита")

        member_ids = sorted(set(user_ids) - {user.id})
        profiles_by_id = await self.profiles.list_by_user_ids(user_ids=set(member_ids))

        for member_id in member_ids:
            profile = profiles_by_id.get(member_id)

            if profile is None or AUDIT_DIRECTION not in profile.directions:
                raise InvalidAuditApplicationError("В группу можно включить только аудиторов")

        previous_member_ids = set(await self.teams.list_user_ids(audit_id=audit_id))
        await self.teams.replace(
            audit_id=audit_id,
            user_ids=member_ids,
        )

        notifications = [
            Notification(
                user_id=member_id,
                audit_id=audit_id,
                text=f"Вас включили в аудиторскую группу по заявке №{audit_id}",
            )
            for member_id in member_ids
            if member_id not in previous_member_ids
        ]
        await self.notifications.add_many(notifications=notifications)
        response = AuditResponse.from_model(audit=audit)
        await self.session.commit()

        return response
