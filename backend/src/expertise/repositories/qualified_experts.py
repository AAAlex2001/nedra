"""Поиск экспертов для заявки."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.enums import UserRole
from src.users.models.expert_certificate import ExpertCertificate
from src.users.models.expert_profile import ExpertProfile
from src.users.models.user import User


class QualifiedExpertRepository:
    """Эксперты с подходящей аттестацией."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def list_for_expertise(
        self,
        *,
        object_code: str | None,
        area_code: str | None,
        expert_category: int | None,
    ) -> list[User]:
        """Найти экспертов с действующими удостоверениями."""

        certificates = select(ExpertCertificate.user_id).where(
            ExpertCertificate.valid_until >= date.today(),
        )

        if object_code is not None:
            certificates = certificates.where(ExpertCertificate.object_code == object_code)

        if area_code is not None:
            certificates = certificates.where(ExpertCertificate.area_code == area_code)

        if expert_category is not None:
            certificates = certificates.where(ExpertCertificate.category <= expert_category)

        statement = (
            select(User)
            .join(ExpertProfile, ExpertProfile.user_id == User.id)
            .where(User.role == UserRole.EXPERT, User.id.in_(certificates))
            .order_by(User.id)
        )
        query_result = await self.session.scalars(statement)

        return list(query_result)
