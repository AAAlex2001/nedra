"""Руководитель группы набирает аудиторов в аудиторскую группу."""

from app.models.expertise import AuditTeamMember, Expertise, ExpertiseStatus
from app.models.notification import Notification
from app.models.user import User
from app.services.experts.repo import ExpertProfileRepository
from app.services.expertise.exceptions import (
    ExpertiseAccessError,
    ExpertiseStateError,
    InvalidExpertiseError,
)
from app.services.expertise.repo import ExpertiseRepository
from app.services.notifications.repo import NotificationRepository

TEAM_STATUSES = (ExpertiseStatus.CONTRACT, ExpertiseStatus.PLAN)


class SetAuditTeamUseCase:
    """Заменить состав группы целиком. Новым участникам уходит уведомление.

    Состав меняется, пока План аудита не отправлен заказчику: в Плане
    заказчик видит ФИО всех аудиторов и может попросить кого-то заменить.
    """

    def __init__(
        self,
        expertises: ExpertiseRepository,
        profiles: ExpertProfileRepository,
        notifications: NotificationRepository,
    ) -> None:
        self.expertises = expertises
        self.profiles = profiles
        self.notifications = notifications

    async def execute(self, lead: User, audit: Expertise, user_ids: list[int]) -> Expertise:
        """Бросает ExpertiseAccessError, ExpertiseStateError, InvalidExpertiseError."""

        if audit.expert_id != lead.id:
            raise ExpertiseAccessError("Группу формирует руководитель аудиторской группы")

        if audit.status not in TEAM_STATUSES:
            raise ExpertiseStateError("Состав группы меняется до отправки Плана аудита")

        unique = []
        for user_id in user_ids:
            if user_id != lead.id and user_id not in unique:
                unique.append(user_id)

        for user_id in unique:
            if not await self.profiles.is_auditor(user_id):
                raise InvalidExpertiseError("В группу можно включить только аудиторов")

        current = {member.user_id for member in audit.team}
        audit.team = [AuditTeamMember(user_id=user_id) for user_id in unique]

        self.notifications.add_all(
            [
                Notification(
                    user_id=user_id,
                    expertise_id=audit.id,
                    text=f"Вас включили в аудиторскую группу по заявке №{audit.id}",
                )
                for user_id in unique
                if user_id not in current
            ]
        )

        return await self.expertises.save(audit)
