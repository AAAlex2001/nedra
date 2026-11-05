"""Изменение контактов пользователя."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repositories.expert_applications import ExpertApplicationRepository
from src.users.contact_validation import normalize_phone
from src.users.exceptions import UserNotFoundError
from src.users.repositories.users import UserRepository
from src.users.site.schemas.update_profile import UpdateProfileRequest
from src.users.site.schemas.user import UserResponse


class UpdateProfileUseCase:
    """Обновление имени и телефона."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        users: UserRepository,
        applications: ExpertApplicationRepository,
    ) -> None:
        """Пользователи и заявки экспертов."""

        self.session = session
        self.users = users
        self.applications = applications

    async def execute(
        self,
        *,
        user_id: int,
        payload: UpdateProfileRequest,
    ) -> UserResponse:
        """Изменить имя и телефон."""

        phone = normalize_phone(phone=payload.phone)
        user = await self.users.get_for_update(user_id=user_id)

        if user is None:
            raise UserNotFoundError()

        user.full_name = payload.full_name
        user.phone = phone
        application = await self.applications.get_by_user_id(user_id=user.id)

        if application is not None:
            application.full_name = user.full_name
            application.phone = user.phone

        response = UserResponse.from_model(user=user)
        await self.session.commit()

        return response
