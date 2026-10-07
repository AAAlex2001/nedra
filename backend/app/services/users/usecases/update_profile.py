"""Пользователь сам меняет имя и телефон в личном кабинете."""

from app.models.user import User
from app.services.experts.repo import ExpertApplicationRepository
from app.services.users.repo import UserRepository
from app.services.users.validators import normalize_phone


class UpdateProfileUseCase:
    """Поменять имя и телефон.

    У эксперта те же данные лежат в заявке, из которой создан аккаунт:
    правим и её, чтобы админка показывала актуальные контакты.
    """

    def __init__(self, users: UserRepository, applications: ExpertApplicationRepository) -> None:
        self.users = users
        self.applications = applications

    async def execute(self, user: User, full_name: str, phone: str) -> User:
        """Бросает InvalidPhoneError."""

        user.full_name = full_name.strip()
        user.phone = normalize_phone(phone)

        application = await self.applications.get_by_user_id(user.id)
        if application is not None:
            application.full_name = user.full_name
            application.phone = user.phone

        return await self.users.save(user)
