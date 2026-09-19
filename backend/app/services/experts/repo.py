"""Репозитории экспертов: заявки на регистрацию и профили."""

from datetime import date

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expert import ApplicationStatus, ExpertApplication, ExpertCertificate, ExpertProfile
from app.models.user import User


class ExpertApplicationRepository:
    """Доступ к таблице expert_applications. Сессию получает снаружи, коммитит сам."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_all(self, status: str | None) -> list[ExpertApplication]:
        """Заявки, новые первыми. Если передан status — только с этим статусом."""

        stmt = select(ExpertApplication).order_by(ExpertApplication.created_at.desc())

        if status:
            stmt = stmt.where(ExpertApplication.status == status)

        result = await self.db.execute(stmt)

        return list(result.scalars().all())

    async def get_by_id(self, application_id: int) -> ExpertApplication | None:
        """Заявка по идентификатору или None."""

        return await self.db.get(ExpertApplication, application_id)

    async def get_by_user_id(self, user_id: int) -> ExpertApplication | None:
        """Заявка, из которой был создан этот пользователь-эксперт, или None."""

        stmt = select(ExpertApplication).where(ExpertApplication.user_id == user_id)
        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def has_pending(self, email: str) -> bool:
        """Есть ли по этому email заявка, которая ещё ждёт проверки."""

        stmt = select(ExpertApplication.id).where(
            ExpertApplication.email == email,
            ExpertApplication.status == ApplicationStatus.PENDING,
        )
        found = await self.db.scalar(stmt)

        return found is not None

    async def add(self, application: ExpertApplication) -> ExpertApplication:
        """Сохранить новую заявку вместе с удостоверениями."""

        self.db.add(application)
        await self.db.commit()
        await self.db.refresh(application)

        return application

    async def save(self, application: ExpertApplication) -> ExpertApplication:
        """Сохранить изменения заявки."""

        await self.db.commit()
        await self.db.refresh(application)

        return application

    async def approve(
        self, application: ExpertApplication, user: User, profile: ExpertProfile
    ) -> ExpertApplication:
        """Создать пользователя и профиль и привязать удостоверения одной транзакцией.

        Если что-то упадёт посередине, не останется пользователя без профиля
        или удостоверений без владельца: commit один на всё.
        """

        self.db.add(user)
        await self.db.flush()

        profile.user_id = user.id
        self.db.add(profile)

        for certificate in application.certificates:
            certificate.user_id = user.id

        application.user_id = user.id

        await self.db.commit()
        await self.db.refresh(application)

        return application


class ExpertProfileRepository:
    """Доступ к профилям и удостоверениям одобренных экспертов."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_user(self, user_id: int) -> ExpertProfile | None:
        """Профиль эксперта по id пользователя или None."""

        return await self.db.get(ExpertProfile, user_id)

    async def list_certificates(self, user_id: int) -> list[ExpertCertificate]:
        """Удостоверения эксперта в порядке добавления."""

        stmt = (
            select(ExpertCertificate)
            .where(ExpertCertificate.user_id == user_id)
            .order_by(ExpertCertificate.id)
        )
        result = await self.db.execute(stmt)

        return list(result.scalars().all())

    async def remove(self, profile: ExpertProfile) -> None:
        """Удалить профиль и удостоверения эксперта одной транзакцией."""

        stmt = delete(ExpertCertificate).where(ExpertCertificate.user_id == profile.user_id)
        await self.db.execute(stmt)
        await self.db.delete(profile)
        await self.db.commit()

    async def get_certificate(self, user_id: int, certificate_id: int) -> ExpertCertificate | None:
        """Удостоверение эксперта по id, только если принадлежит этому эксперту."""

        stmt = select(ExpertCertificate).where(
            ExpertCertificate.id == certificate_id,
            ExpertCertificate.user_id == user_id,
        )
        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def list_certified(
        self, object_code: str, area_code: str, max_category: int
    ) -> list[User]:
        """Эксперты с действующим удостоверением под пару и категорией не хуже требуемой."""

        today = date.today()

        stmt = (
            select(User)
            .join(ExpertCertificate, ExpertCertificate.user_id == User.id)
            .where(
                ExpertCertificate.object_code == object_code,
                ExpertCertificate.area_code == area_code,
                ExpertCertificate.category <= max_category,
                ExpertCertificate.valid_until >= today,
            )
            .distinct()
            .order_by(User.full_name)
        )
        result = await self.db.execute(stmt)

        return list(result.scalars().all())
