"""Изменение направлений работы."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repositories.expert_applications import ExpertApplicationRepository
from src.users.attestation_validation import validate_directions
from src.users.exceptions import ExpertNotFoundError
from src.users.options import AUDIT_DIRECTION
from src.users.repositories.expert_certificates import ExpertCertificateRepository
from src.users.repositories.expert_profiles import ExpertProfileRepository
from src.users.site.schemas.expert_profile import ExpertProfileResponse


class UpdateExpertDirectionsUseCase:
    """Выбор направлений работы эксперта."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        profiles: ExpertProfileRepository,
        certificates: ExpertCertificateRepository,
        applications: ExpertApplicationRepository,
    ) -> None:
        """Профили, удостоверения и заявки."""

        self.session = session
        self.profiles = profiles
        self.certificates = certificates
        self.applications = applications

    async def execute(
        self,
        *,
        user_id: int,
        directions: list[str],
    ) -> ExpertProfileResponse:
        """Обновить направления работы."""

        validate_directions(directions=directions)
        profile = await self.profiles.get_for_update(user_id=user_id)

        if profile is None:
            raise ExpertNotFoundError()

        profile.directions = directions

        if AUDIT_DIRECTION not in directions:
            profile.audit_lead = False

        application = await self.applications.get_by_user_id(user_id=user_id)

        if application is not None:
            application.directions = directions

        certificates = await self.certificates.list_for_user(user_id=user_id)
        response = ExpertProfileResponse.from_model(
            profile=profile,
            certificates=certificates,
        )
        await self.session.commit()

        return response
