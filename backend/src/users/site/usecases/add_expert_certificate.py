"""Добавление удостоверения эксперта."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.users.attestation_validation import (
    validate_certificate,
    validate_certificate_unique,
)
from src.users.exceptions import ExpertNotFoundError
from src.users.models.expert_certificate import ExpertCertificate
from src.users.models.user import User
from src.users.repositories.expert_certificates import ExpertCertificateRepository
from src.users.repositories.expert_profiles import ExpertProfileRepository
from src.users.site.expert_letters import ExpertLetters
from src.users.site.schemas.save_expert_certificate import (
    SaveExpertCertificateRequest,
    SaveExpertCertificateResponse,
)


class AddExpertCertificateUseCase:
    """Добавление сведений об аттестации."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        profiles: ExpertProfileRepository,
        certificates: ExpertCertificateRepository,
        letters: ExpertLetters,
    ) -> None:
        """Профили, удостоверения и письма."""

        self.session = session
        self.profiles = profiles
        self.certificates = certificates
        self.letters = letters

    async def execute(
        self,
        *,
        user: User,
        payload: SaveExpertCertificateRequest,
    ) -> SaveExpertCertificateResponse:
        """Добавить удостоверение эксперта."""

        validate_certificate(
            area_code=payload.area_code,
            object_code=payload.object_code,
            category=payload.category,
        )
        profile = await self.profiles.get_for_update(user_id=user.id)

        if profile is None:
            raise ExpertNotFoundError()

        certificates = await self.certificates.list_for_user(user_id=user.id)
        validate_certificate_unique(
            area_code=payload.area_code,
            object_code=payload.object_code,
            certificates=certificates,
        )
        certificate = ExpertCertificate(
            user_id=user.id,
            area_code=payload.area_code,
            object_code=payload.object_code,
            category=payload.category,
            valid_until=payload.valid_until,
            number=payload.number,
        )
        await self.certificates.save(certificate=certificate)
        response = SaveExpertCertificateResponse.from_model(
            profile=profile,
            certificates=[*certificates, certificate],
        )
        await self.session.commit()
        await self.letters.send_certificate_changed(
            user=user,
            certificate=certificate,
            action="добавил",
        )

        return response
