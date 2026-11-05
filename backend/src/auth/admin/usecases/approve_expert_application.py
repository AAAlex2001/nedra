"""Одобрение заявки эксперта."""

from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.admin.exceptions import (
    ExpertApplicationAlreadyReviewedError,
    ExpertApplicationNotFoundError,
)
from src.auth.admin.expert_application_letters import ExpertApplicationReviewLetters
from src.auth.admin.schemas.expert_application import ExpertApplicationResponse
from src.auth.enums import ApplicationStatus
from src.auth.repositories.expert_applications import ExpertApplicationRepository
from src.users.enums import UserRole
from src.users.exceptions import EmailAlreadyTakenError
from src.users.models.expert_profile import ExpertProfile
from src.users.models.user import User
from src.users.repositories.expert_certificates import ExpertCertificateRepository
from src.users.repositories.expert_profiles import ExpertProfileRepository
from src.users.repositories.users import UserRepository


class ApproveExpertApplicationUseCase:
    """Создание аккаунта по одобренной заявке."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        applications: ExpertApplicationRepository,
        users: UserRepository,
        profiles: ExpertProfileRepository,
        certificates: ExpertCertificateRepository,
        letters: ExpertApplicationReviewLetters,
    ) -> None:
        """Заявки, аккаунты, удостоверения и письма."""

        self.session = session
        self.applications = applications
        self.users = users
        self.profiles = profiles
        self.certificates = certificates
        self.letters = letters

    async def execute(self, *, application_id: int) -> ExpertApplicationResponse:
        """Одобрить регистрацию эксперта."""

        application = await self.applications.get_for_update(application_id=application_id)

        if application is None:
            raise ExpertApplicationNotFoundError()

        if application.status != ApplicationStatus.PENDING:
            raise ExpertApplicationAlreadyReviewedError()

        email = application.email

        if await self.users.get_by_email(email=email) is not None:
            raise EmailAlreadyTakenError()

        certificates = await self.certificates.list_for_application(application_id=application_id)
        user = User(
            email=email,
            password_hash=application.password_hash,
            full_name=application.full_name,
            phone=application.phone,
            role=UserRole.EXPERT,
        )

        try:
            await self.users.add(user=user)
            profile = ExpertProfile(
                user_id=user.id,
                directions=application.directions,
                audit_lead=False,
            )
            await self.profiles.add(profile=profile)

            for certificate in certificates:
                certificate.user_id = user.id

            application.user_id = user.id
            application.status = ApplicationStatus.APPROVED
            application.reviewed_at = datetime.now(UTC)
            response = ExpertApplicationResponse.from_model(
                application=application,
                certificates=certificates,
            )
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()

            if await self.users.get_by_email(email=email) is not None:
                raise EmailAlreadyTakenError() from None

            raise

        await self.letters.send_application_approved(application=application)

        return response
