"""Репозиторий заявок кандидатов: только запросы к таблице commission_applications."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commission import CommissionApplication


class CommissionRepository:
    """Доступ к заявкам кандидатов. Сессию получает снаружи, коммитит сам."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_all(self) -> list[CommissionApplication]:
        """Все заявки, новые первыми."""

        stmt = select(CommissionApplication).order_by(CommissionApplication.created_at.desc())
        result = await self.db.execute(stmt)

        return list(result.scalars().all())

    async def get_by_id(self, application_id: int) -> CommissionApplication | None:
        """Заявка по идентификатору или None."""

        return await self.db.get(CommissionApplication, application_id)

    async def add(self, application: CommissionApplication) -> CommissionApplication:
        """Сохранить новую заявку."""

        self.db.add(application)
        await self.db.commit()
        await self.db.refresh(application)

        return application

    async def delete(self, application: CommissionApplication) -> None:
        """Удалить заявку."""

        await self.db.delete(application)
        await self.db.commit()
