"""Добавление удостоверения администратором."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.users.attestation_validation import validate_certificate, validate_certificate_unique
from src.users.exceptions import ExpertNotFoundError
from src.users.models.expert_certificate import ExpertCertificate
from src.users.repositories.expert_certificates import ExpertCertificateRepository
from src.users.repositories.expert_profiles import ExpertProfileRepository
from src.users.schemas.expert_certificate import ExpertCertificateRequest


class AddExpertCertificateUseCase:
    """Добавление удостоверения выбранному эксперту."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        profiles: ExpertProfileRepository,
        certificates: ExpertCertificateRepository,
    ) -> None:
        """Профили и удостоверения."""

        self.session = session
        self.profiles = profiles
        self.certificates = certificates

    async def execute(
        self,
        *,
        user_id: int,
        payload: ExpertCertificateRequest,
    ) -> None:
        """Добавить удостоверение эксперта."""

        validate_certificate(
            area_code=payload.area_code,
            object_code=payload.object_code,
            category=payload.category,
        )
        profile = await self.profiles.get_for_update(user_id=user_id)

        if profile is None:
            raise ExpertNotFoundError()

        certificates = await self.certificates.list_for_user(user_id=user_id)
        validate_certificate_unique(
            area_code=payload.area_code,
            object_code=payload.object_code,
            certificates=certificates,
        )
        certificate = ExpertCertificate(
            user_id=user_id,
            area_code=payload.area_code,
            object_code=payload.object_code,
            category=payload.category,
            valid_until=payload.valid_until,
            number=payload.number,
        )
        await self.certificates.save(certificate=certificate)
        await self.session.commit()
