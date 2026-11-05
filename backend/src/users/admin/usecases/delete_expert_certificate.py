"""Удаление удостоверения администратором."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.users.exceptions import (
    CertificateNotFoundError,
    ExpertNotFoundError,
    InvalidCertificateError,
)
from src.users.repositories.expert_certificates import ExpertCertificateRepository
from src.users.repositories.expert_profiles import ExpertProfileRepository


class DeleteExpertCertificateUseCase:
    """Удаление удостоверения выбранного эксперта."""

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
        certificate_id: int,
    ) -> None:
        """Удалить удостоверение эксперта."""

        profile = await self.profiles.get_for_update(user_id=user_id)

        if profile is None:
            raise ExpertNotFoundError()

        certificate = await self.certificates.get_for_user(
            user_id=user_id,
            certificate_id=certificate_id,
        )

        if certificate is None:
            raise CertificateNotFoundError()

        certificates = await self.certificates.list_for_user(user_id=user_id)

        if len(certificates) <= 1:
            raise InvalidCertificateError("Должно остаться хотя бы одно удостоверение")

        await self.certificates.remove(certificate=certificate)
        await self.session.commit()
