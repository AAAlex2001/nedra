"""Подбор участников аудиторской группы."""

from src.audit.exceptions import AuditAccessError
from src.audit.site.schemas.audit_plan import AuditTeamMemberResponse
from src.users.models.user import User
from src.users.repositories.expert_certificates import ExpertCertificateRepository
from src.users.repositories.expert_profiles import ExpertProfileRepository


class ListAuditorsUseCase:
    """Аудиторы для выбора руководителем."""

    def __init__(
        self,
        *,
        profiles: ExpertProfileRepository,
        certificates: ExpertCertificateRepository,
    ) -> None:
        """Профили и удостоверения аудиторов."""

        self.profiles = profiles
        self.certificates = certificates

    async def execute(self, *, user: User) -> list[AuditTeamMemberResponse]:
        """Получить аудиторов для группы."""

        profile = await self.profiles.get_by_user_id(user_id=user.id)

        if profile is None or not profile.audit_lead:
            raise AuditAccessError("Список аудиторов доступен руководителю группы")

        auditors = await self.profiles.list_auditors()
        certificates_by_user_id = await self.certificates.list_for_users(
            user_ids={auditor.id for auditor in auditors},
        )
        members = []

        for auditor in auditors:
            if auditor.id == user.id:
                continue

            certificates = certificates_by_user_id.get(auditor.id, [])
            member = AuditTeamMemberResponse(
                user_id=auditor.id,
                full_name=auditor.full_name,
                areas=sorted({certificate.area_code for certificate in certificates}),
                lead=False,
            )
            members.append(member)

        return members
