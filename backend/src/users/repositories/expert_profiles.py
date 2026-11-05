"""Профили экспертов."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.enums import UserRole
from src.users.models.expert_profile import ExpertProfile
from src.users.models.user import User
from src.users.options import AUDIT_DIRECTION


class ExpertProfileRepository:
    """Аттестованные эксперты и руководители аудита."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def get_by_user_id(self, *, user_id: int) -> ExpertProfile | None:
        """Найти профиль эксперта."""

        return await self.session.get(ExpertProfile, user_id)

    async def get_for_update(self, *, user_id: int) -> ExpertProfile | None:
        """Получить профиль для изменения."""

        statement = select(ExpertProfile).where(ExpertProfile.user_id == user_id).with_for_update()
        query_result = await self.session.scalars(statement)

        return query_result.one_or_none()

    async def list_audit_leads(self) -> list[User]:
        """Получить руководителей аудиторских групп."""

        statement = (
            select(User)
            .join(
                ExpertProfile,
                ExpertProfile.user_id == User.id,
            )
            .where(
                User.role == UserRole.EXPERT,
                ExpertProfile.audit_lead.is_(True),
            )
            .order_by(User.id)
        )
        query_result = await self.session.scalars(statement)

        return list(query_result)

    async def list_by_user_ids(self, *, user_ids: set[int]) -> dict[int, ExpertProfile]:
        """Получить профили выбранных экспертов."""

        if not user_ids:
            return {}

        statement = select(ExpertProfile).where(ExpertProfile.user_id.in_(user_ids))
        query_result = await self.session.scalars(statement)

        return {profile.user_id: profile for profile in query_result}

    async def list_all(self) -> list[ExpertProfile]:
        """Получить профили от новых к старым."""

        statement = select(ExpertProfile).order_by(
            ExpertProfile.approved_at.desc(),
            ExpertProfile.user_id.desc(),
        )
        query_result = await self.session.scalars(statement)

        return list(query_result)

    async def list_auditors(self) -> list[User]:
        """Получить экспертов с направлением аудита."""

        statement = (
            select(User, ExpertProfile)
            .join(ExpertProfile, ExpertProfile.user_id == User.id)
            .where(User.role == UserRole.EXPERT)
            .order_by(User.full_name, User.id)
        )
        query_result = await self.session.execute(statement)

        return [user for user, profile in query_result if AUDIT_DIRECTION in profile.directions]

    async def add(self, *, profile: ExpertProfile) -> None:
        """Добавить профиль эксперта."""

        self.session.add(profile)
        await self.session.flush()
