"""Участники аудиторской группы."""

from pydantic import BaseModel

from src.users.models.expert_certificate import ExpertCertificate
from src.users.models.user import User


class AuditTeamMemberResponse(BaseModel):
    """Участник аудиторской группы."""

    user_id: int
    full_name: str
    areas: list[str]
    lead: bool

    @classmethod
    def from_model(
        cls,
        *,
        user: User,
        certificates: list[ExpertCertificate],
        is_lead: bool,
    ) -> "AuditTeamMemberResponse":
        """Подготовить сведения об участнике."""

        return cls(
            user_id=user.id,
            full_name=user.full_name,
            areas=sorted({certificate.area_code for certificate in certificates}),
            lead=is_lead,
        )
