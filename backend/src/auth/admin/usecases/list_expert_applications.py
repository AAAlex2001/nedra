"""Просмотр заявок экспертов."""

from src.auth.admin.schemas.expert_application import ExpertApplicationResponse
from src.auth.enums import ApplicationStatus
from src.auth.repositories.expert_applications import ExpertApplicationRepository
from src.users.repositories.expert_certificates import ExpertCertificateRepository
from src.users.repositories.expert_profiles import ExpertProfileRepository


class ListExpertApplicationsUseCase:
    """Список заявок для администратора."""

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

    async def execute(self, *, status: ApplicationStatus | None) -> list[ExpertApplicationResponse]:
        """Получить заявки на регистрацию."""

        applications = await self.applications.list_all(status=status)
        certificates = await self.certificates.list_for_applications(
            application_ids={application.id for application in applications},
        )
        profiles = await self.profiles.list_by_user_ids(
            user_ids={
                application.user_id
                for application in applications
                if application.user_id is not None
            },
        )
        responses = []

        for application in applications:
            profile = profiles.get(application.user_id)
            responses.append(
                ExpertApplicationResponse.from_model(
                    application=application,
                    certificates=certificates.get(application.id, []),
                    audit_lead=profile.audit_lead if profile is not None else False,
                )
            )

        return responses
