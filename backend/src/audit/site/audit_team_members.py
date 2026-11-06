"""Состав аудиторской группы."""

from src.audit.models.audit import Audit
from src.audit.repositories.audit_teams import AuditTeamRepository
from src.audit.site.schemas.audit_team import AuditTeamMemberResponse
from src.users.exceptions import UserNotFoundError
from src.users.repositories.expert_certificates import ExpertCertificateRepository
from src.users.repositories.users import UserRepository


class AuditTeamMembers:
    """Имена и аттестация участников группы."""

    def __init__(
        self,
        *,
        teams: AuditTeamRepository,
        users: UserRepository,
        certificates: ExpertCertificateRepository,
    ) -> None:
        """Группа, аккаунты и удостоверения."""

        self.teams = teams
        self.users = users
        self.certificates = certificates

    async def list_for_audit(self, *, audit: Audit) -> list[AuditTeamMemberResponse]:
        """Получить группу, начиная с руководителя."""

        user_ids = await self.teams.list_user_ids(audit_id=audit.id)
        if audit.lead_id is not None:
            user_ids = [
                audit.lead_id,
                *[user_id for user_id in user_ids if user_id != audit.lead_id],
            ]

        users_by_id = await self.users.list_by_ids(user_ids=set(user_ids))
        certificates_by_user_id = await self.certificates.list_for_users(user_ids=set(user_ids))
        members = []

        for user_id in user_ids:
            user = users_by_id.get(user_id)
            if user is None:
                raise UserNotFoundError()

            user_certificates = certificates_by_user_id.get(user_id, [])
            members.append(
                AuditTeamMemberResponse.from_model(
                    user=user,
                    certificates=user_certificates,
                    is_lead=user.id == audit.lead_id,
                ),
            )

        return members
