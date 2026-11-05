"""Рассмотрение заявки эксперта."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from src.auth.enums import ApplicationStatus
from src.auth.models.expert_application import ExpertApplication
from src.users.models.expert_certificate import ExpertCertificate
from src.users.schemas.expert_certificate import ExpertCertificateResponse


class RejectExpertApplicationRequest(BaseModel):
    """Причина отклонения заявки."""

    comment: str = Field(
        min_length=3,
        max_length=1000,
    )


class ExpertApplicationResponse(BaseModel):
    """Заявка эксперта для администратора."""

    id: int
    email: EmailStr
    full_name: str
    phone: str
    directions: list[str]
    audit_lead: bool
    status: ApplicationStatus
    admin_comment: str | None
    user_id: int | None
    created_at: datetime
    reviewed_at: datetime | None
    certificates: list[ExpertCertificateResponse]

    @classmethod
    def from_model(
        cls,
        *,
        application: ExpertApplication,
        certificates: list[ExpertCertificate],
        audit_lead: bool = False,
    ) -> "ExpertApplicationResponse":
        """Подготовить заявку для просмотра."""

        return cls(
            id=application.id,
            email=application.email,
            full_name=application.full_name,
            phone=application.phone,
            directions=application.directions,
            audit_lead=audit_lead,
            status=ApplicationStatus(application.status),
            admin_comment=application.admin_comment,
            user_id=application.user_id,
            created_at=application.created_at,
            reviewed_at=application.reviewed_at,
            certificates=[
                ExpertCertificateResponse.from_model(certificate=certificate)
                for certificate in certificates
            ],
        )
