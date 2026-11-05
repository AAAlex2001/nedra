"""Просмотр экспертов администратором."""

from src.users.admin.schemas.expert import ExpertResponse
from src.users.exceptions import ExpertNotFoundError
from src.users.repositories.expert_certificates import ExpertCertificateRepository
from src.users.repositories.expert_profiles import ExpertProfileRepository
from src.users.repositories.users import UserRepository


class ListExpertsUseCase:
    """Список зарегистрированных экспертов."""

    def __init__(
        self,
        *,
        users: UserRepository,
        profiles: ExpertProfileRepository,
        certificates: ExpertCertificateRepository,
    ) -> None:
        """Аккаунты, профили и удостоверения."""

        self.users = users
        self.profiles = profiles
        self.certificates = certificates

    async def execute(self) -> list[ExpertResponse]:
        """Получить экспертов с удостоверениями."""

        profiles = await self.profiles.list_all()
        user_ids = {profile.user_id for profile in profiles}

        users_by_id = await self.users.list_by_ids(user_ids=user_ids)
        certificates_by_user_id = await self.certificates.list_for_users(user_ids=user_ids)

        experts = []

        for profile in profiles:
            user = users_by_id.get(profile.user_id)

            if user is None:
                raise ExpertNotFoundError()

            certificates = certificates_by_user_id.get(user.id, [])
            expert = ExpertResponse.from_model(
                user=user,
                profile=profile,
                certificates=certificates,
            )
            experts.append(expert)

        return experts
