"""Изменение эксперта администратором."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repositories.expert_applications import ExpertApplicationRepository
from src.users.admin.schemas.expert import ExpertResponse, UpdateExpertRequest
from src.users.attestation_validation import validate_directions
from src.users.contact_validation import normalize_phone
from src.users.enums import UserRole
from src.users.exceptions import ExpertNotFoundError
from src.users.options import AUDIT_DIRECTION
from src.users.repositories.expert_certificates import ExpertCertificateRepository
from src.users.repositories.expert_profiles import ExpertProfileRepository
from src.users.repositories.users import UserRepository


class UpdateExpertUseCase:
    """Изменение контактов и прав эксперта."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        users: UserRepository,
        profiles: ExpertProfileRepository,
        certificates: ExpertCertificateRepository,
        applications: ExpertApplicationRepository,
    ) -> None:
        """Данные эксперта и заявки на регистрацию."""

        self.session = session
        self.users = users
        self.profiles = profiles
        self.certificates = certificates
        self.applications = applications

    async def execute(
        self,
        *,
        user_id: int,
        payload: UpdateExpertRequest,
    ) -> ExpertResponse:
        """Изменить профиль эксперта."""

        validate_directions(directions=payload.directions)
        phone = normalize_phone(phone=payload.phone)
        user = await self.users.get_for_update(user_id=user_id)

        if user is None or user.role != UserRole.EXPERT:
            raise ExpertNotFoundError()

        profile = await self.profiles.get_for_update(user_id=user_id)

        if profile is None:
            raise ExpertNotFoundError()

        user.full_name = payload.full_name
        user.phone = phone
        profile.directions = payload.directions
        profile.audit_lead = payload.audit_lead and AUDIT_DIRECTION in payload.directions
        application = await self.applications.get_by_user_id(user_id=user_id)

        if application is not None:
            application.full_name = user.full_name
            application.phone = user.phone
            application.directions = profile.directions

        certificates = await self.certificates.list_for_user(user_id=user_id)
        response = ExpertResponse.from_model(
            user=user,
            profile=profile,
            certificates=certificates,
        )
        await self.session.commit()

        return response
