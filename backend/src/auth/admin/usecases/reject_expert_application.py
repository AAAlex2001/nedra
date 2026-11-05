"""Отклонение заявки эксперта."""

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.admin.exceptions import (
    ExpertApplicationAlreadyReviewedError,
    ExpertApplicationNotFoundError,
)
from src.auth.admin.expert_application_letters import ExpertApplicationReviewLetters
from src.auth.admin.schemas.expert_application import (
    ExpertApplicationResponse,
    RejectExpertApplicationRequest,
)
from src.auth.enums import ApplicationStatus
from src.auth.repositories.expert_applications import ExpertApplicationRepository
from src.users.repositories.expert_certificates import ExpertCertificateRepository


class RejectExpertApplicationUseCase:
    """Отклонение регистрации с причиной."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        applications: ExpertApplicationRepository,
        certificates: ExpertCertificateRepository,
        letters: ExpertApplicationReviewLetters,
    ) -> None:
        """Заявки, удостоверения и письма."""

        self.session = session
        self.applications = applications
        self.certificates = certificates
        self.letters = letters

    async def execute(
        self,
        *,
        application_id: int,
        payload: RejectExpertApplicationRequest,
    ) -> ExpertApplicationResponse:
        """Отклонить заявку эксперта."""

        application = await self.applications.get_for_update(application_id=application_id)

        if application is None:
            raise ExpertApplicationNotFoundError()

        if application.status != ApplicationStatus.PENDING:
            raise ExpertApplicationAlreadyReviewedError()

        application.status = ApplicationStatus.REJECTED
        application.admin_comment = payload.comment.strip()
        application.reviewed_at = datetime.now(UTC)
        certificates = await self.certificates.list_for_application(application_id=application_id)
        response = ExpertApplicationResponse.from_model(
            application=application,
            certificates=certificates,
        )
        await self.session.commit()
        await self.letters.send_application_rejected(application=application)

        return response
