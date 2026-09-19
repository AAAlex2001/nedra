"""Сценарий отклонения заявки эксперта."""

from datetime import datetime, timezone

from app.models.expert import ApplicationStatus, ExpertApplication
from app.services.experts.exceptions import (
    ApplicationAlreadyReviewedError,
    ApplicationNotFoundError,
)
from app.services.experts.repo import ExpertApplicationRepository


class RejectExpertApplicationUseCase:
    """Отклонить заявку с причиной, которую увидит эксперт."""

    def __init__(self, applications: ExpertApplicationRepository) -> None:
        self.applications = applications

    async def execute(self, application_id: int, comment: str) -> ExpertApplication:
        """Отклонить заявку. Бросает ApplicationNotFoundError, ApplicationAlreadyReviewedError."""

        application = await self.applications.get_by_id(application_id)
        if application is None:
            raise ApplicationNotFoundError(f"Заявка {application_id} не найдена")

        if application.status != ApplicationStatus.PENDING:
            raise ApplicationAlreadyReviewedError("Заявка уже рассмотрена")

        application.status = ApplicationStatus.REJECTED
        application.admin_comment = comment.strip()
        application.reviewed_at = datetime.now(timezone.utc)

        return await self.applications.save(application)
