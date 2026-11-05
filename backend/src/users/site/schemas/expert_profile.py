"""Профиль эксперта в кабинете."""

from datetime import datetime

from pydantic import BaseModel, Field

from src.users.models.expert_certificate import ExpertCertificate
from src.users.models.expert_profile import ExpertProfile
from src.users.schemas.expert_certificate import ExpertCertificateResponse


class UpdateExpertDirectionsRequest(BaseModel):
    """Направления работы эксперта."""

    directions: list[str] = Field(min_length=1)


class ExpertProfileResponse(BaseModel):
    """Направления работы и удостоверения."""

    directions: list[str]
    approved_at: datetime
    certificates: list[ExpertCertificateResponse]

    @classmethod
    def from_model(
        cls,
        *,
        profile: ExpertProfile,
        certificates: list[ExpertCertificate],
    ) -> "ExpertProfileResponse":
        """Подготовить профиль для кабинета."""

        return cls(
            directions=profile.directions,
            approved_at=profile.approved_at,
            certificates=[
                ExpertCertificateResponse.from_model(certificate=certificate)
                for certificate in certificates
            ],
        )
