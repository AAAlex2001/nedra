"""Просмотр профиля эксперта."""

from src.users.exceptions import ExpertNotFoundError
from src.users.repositories.expert_certificates import ExpertCertificateRepository
from src.users.repositories.expert_profiles import ExpertProfileRepository
from src.users.site.schemas.expert_profile import ExpertProfileResponse


class GetExpertProfileUseCase:
    """Профиль зарегистрированного эксперта."""

    def __init__(
        self,
        *,
        profiles: ExpertProfileRepository,
        certificates: ExpertCertificateRepository,
    ) -> None:
        """Профили и удостоверения."""

        self.profiles = profiles
        self.certificates = certificates

    async def execute(self, *, user_id: int) -> ExpertProfileResponse:
        """Получить профиль эксперта."""

        profile = await self.profiles.get_by_user_id(user_id=user_id)

        if profile is None:
            raise ExpertNotFoundError()

        certificates = await self.certificates.list_for_user(user_id=user_id)

        return ExpertProfileResponse.from_model(
            profile=profile,
            certificates=certificates,
        )
