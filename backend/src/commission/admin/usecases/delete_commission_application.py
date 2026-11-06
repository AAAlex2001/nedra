"""Удаление заявки кандидата."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.commission.admin.exceptions import CommissionApplicationNotFoundError
from src.commission.repositories.commission_applications import (
    CommissionApplicationRepository,
)


class DeleteCommissionApplicationUseCase:
    """Удаление заявки администратором."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        applications: CommissionApplicationRepository,
    ) -> None:
        """Зависимости удаления заявки."""

        self.session = session
        self.applications = applications

    async def execute(self, *, application_id: int) -> None:
        """Удалить заявку кандидата."""

        was_deleted = await self.applications.delete(application_id=application_id)

        if not was_deleted:
            raise CommissionApplicationNotFoundError()

        await self.session.commit()
