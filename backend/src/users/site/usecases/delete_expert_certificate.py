"""Удаление удостоверения эксперта."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.users.exceptions import (
    CertificateNotFoundError,
    ExpertNotFoundError,
    InvalidCertificateError,
)
from src.users.models.user import User
from src.users.repositories.expert_certificates import ExpertCertificateRepository
from src.users.repositories.expert_profiles import ExpertProfileRepository
from src.users.site.expert_letters import ExpertLetters
from src.users.site.schemas.expert_profile import ExpertProfileResponse


class DeleteExpertCertificateUseCase:
    """Удаление сведений об аттестации."""

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
    ) -> ExpertProfileResponse:
        """Удалить удостоверение эксперта."""

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

        if len(certificates) <= 1:
            raise InvalidCertificateError("Должно остаться хотя бы одно удостоверение")

        await self.certificates.remove(certificate=certificate)
        remaining_certificates = [
            saved_certificate
            for saved_certificate in certificates
            if saved_certificate.id != certificate_id
        ]
        response = ExpertProfileResponse.from_model(
            profile=profile,
            certificates=remaining_certificates,
        )
        await self.session.commit()
        await self.letters.send_certificate_changed(
            user=user,
            certificate=certificate,
            action="удалил",
        )

        return response
