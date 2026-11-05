"""Просмотр заявки эксперта."""

from src.auth.admin.exceptions import ExpertApplicationNotFoundError
from src.auth.admin.schemas.expert_application import ExpertApplicationResponse
from src.auth.repositories.expert_applications import ExpertApplicationRepository
from src.users.repositories.expert_certificates import ExpertCertificateRepository
from src.users.repositories.expert_profiles import ExpertProfileRepository


class GetExpertApplicationUseCase:
    """Заявка эксперта для администратора."""

    def __init__(
        self,
        *,
        applications: ExpertApplicationRepository,
        certificates: ExpertCertificateRepository,
        profiles: ExpertProfileRepository,
    ) -> None:
        """Заявки, удостоверения и профили."""

        self.applications = applications
        self.certificates = certificates
        self.profiles = profiles

    async def execute(self, *, application_id: int) -> ExpertApplicationResponse:
        """Получить заявку эксперта."""

        application = await self.applications.get_by_id(application_id=application_id)

        if application is None:
            raise ExpertApplicationNotFoundError()

        certificates = await self.certificates.list_for_application(application_id=application_id)
        audit_lead = False

        if application.user_id is not None:
            profile = await self.profiles.get_by_user_id(user_id=application.user_id)

            if profile is not None:
                audit_lead = profile.audit_lead

        return ExpertApplicationResponse.from_model(
            application=application,
            certificates=certificates,
            audit_lead=audit_lead,
        )
