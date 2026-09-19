"""Сценарий одобрения заявки эксперта."""

from datetime import datetime, timezone

from app.models.expert import ApplicationStatus, ExpertApplication, ExpertProfile
from app.models.user import User, UserRole
from app.services.experts.exceptions import (
    AlreadyExpertError,
    ApplicationAlreadyReviewedError,
    ApplicationNotFoundError,
)
from app.services.experts.repo import ExpertApplicationRepository, ExpertProfileRepository
from app.services.users.repo import UserRepository


class ApproveExpertApplicationUseCase:
    """Создать профиль эксперта из заявки.

    Если заявку подал вошедший заказчик или человек с уже существующим
    аккаунтом, профиль привязывается к этому аккаунту, пароль остаётся прежним.
    Иначе создаётся новый пользователь с паролем из заявки.
    """

    def __init__(
        self,
        applications: ExpertApplicationRepository,
        users: UserRepository,
        profiles: ExpertProfileRepository,
    ) -> None:
        self.applications = applications
        self.users = users
        self.profiles = profiles

    async def execute(self, application_id: int) -> ExpertApplication:
        """Одобрить заявку. Бросает ApplicationNotFoundError, ApplicationAlreadyReviewedError, AlreadyExpertError."""

        application = await self.applications.get_by_id(application_id)
        if application is None:
            raise ApplicationNotFoundError(f"Заявка {application_id} не найдена")

        if application.status != ApplicationStatus.PENDING:
            raise ApplicationAlreadyReviewedError("Заявка уже рассмотрена")

        user = await self.find_account(application)
        if user is None:
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

    async def find_account(self, application: ExpertApplication) -> User | None:
        """Аккаунт, к которому привязать профиль: из заявки или по email. Уже эксперт — ошибка."""

        user = None
        if application.user_id is not None:
            user = await self.users.get_by_id(application.user_id)

        if user is None:
            user = await self.users.get_by_email(application.email)

        if user is None:
            return None

        profile = await self.profiles.get_by_user(user.id)
        if profile is not None:
            raise AlreadyExpertError(f"У аккаунта {user.email} уже есть профиль эксперта")

        return user
