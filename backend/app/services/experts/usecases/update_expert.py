"""Правка данных эксперта из админки."""

from app.models.expert import ExpertProfile
from app.models.user import User
from app.schemas.expert import CertificateUpdateSchema, ExpertUpdateSchema
from app.services.experts.exceptions import CertificateNotFoundError, ExpertNotFoundError
from app.services.experts.repo import ExpertApplicationRepository, ExpertProfileRepository
from app.services.experts.validators import validate_certificate, validate_directions
from app.services.users.repo import UserRepository
from app.services.users.validators import normalize_phone


class UpdateExpertUseCase:
    """Поменять имя, телефон и направления эксперта.

    Направления дублируются в заявке, из которой создан профиль, поэтому
    правим обе записи: иначе в админке останется старый список.
    """

    def __init__(
        self,
        users: UserRepository,
        profiles: ExpertProfileRepository,
        applications: ExpertApplicationRepository,
    ) -> None:
        self.users = users
        self.profiles = profiles
        self.applications = applications

    async def execute(self, user_id: int, data: ExpertUpdateSchema) -> tuple[User, ExpertProfile]:
        """Бросает ExpertNotFoundError, InvalidDirectionError, InvalidPhoneError."""

        user = await self.users.get_by_id(user_id)
        profile = await self.profiles.get_by_user(user_id)
        if user is None or profile is None:
            raise ExpertNotFoundError(f"Эксперт {user_id} не найден")

        validate_directions(data.directions)

        user.full_name = data.full_name.strip()
        user.phone = normalize_phone(data.phone)
        profile.directions = data.directions

        application = await self.applications.get_by_user_id(user_id)
        if application is not None:
            application.full_name = user.full_name
            application.phone = user.phone
            application.directions = data.directions

        await self.profiles.save()

        return user, profile


class UpdateCertificateUseCase:
    """Поменять область, объект, категорию или срок удостоверения."""

    def __init__(self, profiles: ExpertProfileRepository) -> None:
        self.profiles = profiles

    async def execute(
        self, user_id: int, certificate_id: int, data: CertificateUpdateSchema
    ) -> None:
        """Бросает CertificateNotFoundError и InvalidCertificateError."""

        certificate = await self.profiles.get_certificate(user_id, certificate_id)
        if certificate is None:
            raise CertificateNotFoundError(f"Удостоверение {certificate_id} не найдено")

        validate_certificate(data.area_code, data.object_code, data.category)

        certificate.area_code = data.area_code
        certificate.object_code = data.object_code
        certificate.category = data.category
        certificate.valid_until = data.valid_until

        await self.profiles.save()


class DeleteCertificateUseCase:
    """Убрать удостоверение у эксперта."""

    def __init__(self, profiles: ExpertProfileRepository) -> None:
        self.profiles = profiles

    async def execute(self, user_id: int, certificate_id: int) -> None:
        """Бросает CertificateNotFoundError."""

        certificate = await self.profiles.get_certificate(user_id, certificate_id)
        if certificate is None:
            raise CertificateNotFoundError(f"Удостоверение {certificate_id} не найдено")

        await self.profiles.remove_certificate(certificate)
