"""Изменение удостоверения эксперта."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.users.attestation_validation import validate_certificate, validate_certificate_unique
from src.users.exceptions import CertificateNotFoundError, ExpertNotFoundError
from src.users.models.user import User
from src.users.repositories.expert_certificates import ExpertCertificateRepository
from src.users.repositories.expert_profiles import ExpertProfileRepository
from src.users.schemas.expert_certificate import ExpertCertificateRequest
from src.users.site.expert_letters import ExpertLetters
from src.users.site.schemas.expert_profile import ExpertProfileResponse


class UpdateExpertCertificateUseCase:
    """Редактирование сведений об аттестации."""

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
        certificate_id: int,
        payload: ExpertCertificateRequest,
    ) -> ExpertProfileResponse:
        """Изменить удостоверение эксперта."""

        validate_certificate(
            area_code=payload.area_code,
            object_code=payload.object_code,
            category=payload.category,
        )
        profile = await self.profiles.get_for_update(user_id=user.id)

        if profile is None:
            raise ExpertNotFoundError()

        certificate = await self.certificates.get_for_user(
            user_id=user.id,
            certificate_id=certificate_id,
        )

        if certificate is None:
            raise CertificateNotFoundError()

        certificates = await self.certificates.list_for_user(user_id=user.id)
        validate_certificate_unique(
            area_code=payload.area_code,
            object_code=payload.object_code,
            certificates=certificates,
            exclude_id=certificate_id,
        )
        certificate.area_code = payload.area_code
        certificate.object_code = payload.object_code
        certificate.category = payload.category
        certificate.valid_until = payload.valid_until
        certificate.number = payload.number
        await self.certificates.save(certificate=certificate)
        response = ExpertProfileResponse.from_model(
            profile=profile,
            certificates=certificates,
        )
        await self.session.commit()
        await self.letters.send_certificate_changed(
            user=user,
            certificate=certificate,
            action="изменил",
        )

        return response
