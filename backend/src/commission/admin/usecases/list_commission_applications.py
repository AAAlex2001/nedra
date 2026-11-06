"""Просмотр заявок кандидатов."""

from src.commission.repositories.commission_applications import (
    CommissionApplicationRepository,
)
from src.commission.schemas.commission_application import CommissionApplicationResponse


class ListCommissionApplicationsUseCase:
    """Заявки кандидатов для администратора."""

    def __init__(self, *, applications: CommissionApplicationRepository) -> None:
        """Репозиторий заявок."""

        self.applications = applications

    async def execute(self) -> list[CommissionApplicationResponse]:
        """Получить заявки кандидатов."""

        applications = await self.applications.list_all()

        return [
            CommissionApplicationResponse.from_model(application=application)
            for application in applications
        ]
