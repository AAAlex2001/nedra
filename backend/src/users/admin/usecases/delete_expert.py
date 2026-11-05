"""Удаление аккаунта эксперта."""

from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.enums import ApplicationStatus
from src.auth.repositories.expert_applications import ExpertApplicationRepository
from src.users.admin.exceptions import ExpertHasActivityError
from src.users.admin.options import DELETED_EXPERT_COMMENT, RELATED_RECORD_SQLSTATES
from src.users.enums import UserRole
from src.users.exceptions import ExpertNotFoundError
from src.users.repositories.expert_profiles import ExpertProfileRepository
from src.users.repositories.users import UserRepository


class DeleteExpertUseCase:
    """Удаление эксперта без истории работ."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        users: UserRepository,
        profiles: ExpertProfileRepository,
        applications: ExpertApplicationRepository,
    ) -> None:
        """Аккаунты, профили и заявки."""

        self.session = session
        self.users = users
        self.profiles = profiles
        self.applications = applications

    async def execute(self, *, user_id: int) -> None:
        """Удалить аккаунт эксперта."""

        user = await self.users.get_for_update(user_id=user_id)

        if user is None or user.role != UserRole.EXPERT:
            raise ExpertNotFoundError()

        profile = await self.profiles.get_for_update(user_id=user_id)

        if profile is None:
            raise ExpertNotFoundError()

        application = await self.applications.get_by_user_id(user_id=user_id)

        if application is not None:
            application.status = ApplicationStatus.REJECTED
            application.admin_comment = DELETED_EXPERT_COMMENT
            application.reviewed_at = datetime.now(UTC)
            application.user_id = None

        try:
            await self.users.delete(user=user)
        except IntegrityError as error:
            await self.session.rollback()

            if error.orig.sqlstate in RELATED_RECORD_SQLSTATES:
                raise ExpertHasActivityError() from None

            raise

        await self.session.commit()
