"""Сценарий одобрения заявки эксперта."""

from datetime import datetime, timezone

from app.models.expert import ApplicationStatus, ExpertApplication, ExpertProfile
from app.models.user import User, UserRole
from app.services.experts.exceptions import (
    ApplicationAlreadyReviewedError,
    ApplicationNotFoundError,
)
from app.services.experts.repo import ExpertApplicationRepository
from app.services.users.exceptions import EmailAlreadyTakenError
from app.services.users.repo import UserRepository


class ApproveExpertApplicationUseCase:
    """Создать аккаунт эксперта из заявки: пользователя, профиль и удостоверения.

    Аккаунт всегда новый: роль у аккаунта одна, поэтому к существующему
    пользователю профиль эксперта не привязываем.
    """

    def __init__(
        self,
        applications: ExpertApplicationRepository,
        users: UserRepository,
    ) -> None:
        self.applications = applications
        self.users = users

    async def execute(self, application_id: int) -> ExpertApplication:
        """Одобрить заявку. Бросает ApplicationNotFoundError, ApplicationAlreadyReviewedError, EmailAlreadyTakenError."""

        application = await self.applications.get_by_id(application_id)
        if application is None:
            raise ApplicationNotFoundError(f"Заявка {application_id} не найдена")

        if application.status != ApplicationStatus.PENDING:
            raise ApplicationAlreadyReviewedError("Заявка уже рассмотрена")

        existing = await self.users.get_by_email(application.email)
        if existing is not None:
            raise EmailAlreadyTakenError(f"Email {application.email} уже занят другим аккаунтом")

        user = User(
            email=application.email,
            password_hash=application.password_hash,
            full_name=application.full_name,
            phone=application.phone,
            role=UserRole.EXPERT,
        )
        profile = ExpertProfile(directions=application.directions)

        application.status = ApplicationStatus.APPROVED
        application.reviewed_at = datetime.now(timezone.utc)

        return await self.applications.approve(application, user, profile)
