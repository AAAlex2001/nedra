"""Доступ к экспертизе."""

from src.expertise.enums import ExpertiseStatus
from src.expertise.exceptions import ExpertiseNotFoundError
from src.expertise.expert_qualification import expert_qualifies
from src.expertise.models.expertise import Expertise
from src.expertise.repositories.expertises import ExpertiseRepository
from src.users.enums import UserRole
from src.users.models.user import User
from src.users.repositories.expert_certificates import ExpertCertificateRepository


class ExpertiseAccess:
    """Проверка участника и квалификации."""

    def __init__(
        self,
        *,
        expertises: ExpertiseRepository,
        certificates: ExpertCertificateRepository,
    ) -> None:
        """Услуга и права участника."""

        self.expertises = expertises
        self.certificates = certificates

    async def get_visible(
        self,
        *,
        expertise_id: int,
        user: User,
    ) -> Expertise:
        """Найти доступную пользователю услугу."""

        expertise = await self.expertises.get_by_id(expertise_id=expertise_id)

        if expertise is None:
            raise ExpertiseNotFoundError()

        if user.role == UserRole.CUSTOMER and expertise.customer_id == user.id:
            return expertise

        if user.role != UserRole.EXPERT:
            raise ExpertiseNotFoundError()

        if expertise.expert_id == user.id:
            return expertise

        if expertise.status == ExpertiseStatus.NEW and expertise.expert_id is None:
            certificates = await self.certificates.list_for_user(user_id=user.id)

            if expert_qualifies(
                expertise=expertise,
                certificates=certificates,
            ):
                return expertise

        raise ExpertiseNotFoundError()
