"""Сценарий подачи заявки кандидата в конкурсную комиссию."""

from app.models.commission import CommissionApplication
from app.schemas.commission import CommissionApplicationInSchema
from app.services.commission.repo import CommissionRepository
from app.services.experts.validators import validate_certificate


class CreateCommissionApplicationUseCase:
    """Проверить аттестации по справочнику и сохранить заявку."""

    def __init__(self, applications: CommissionRepository) -> None:
        self.applications = applications

    async def execute(self, data: CommissionApplicationInSchema) -> CommissionApplication:
        """Создать заявку. Бросает InvalidCertificateError."""

        attestations = []
        for item in data.attestations:
            validate_certificate(item.area_code, item.object_code, item.category)
            attestations.append(item.model_dump())

        application = CommissionApplication(
            full_name=data.full_name.strip(),
            phone=data.phone.strip(),
            email=data.email,
            attestations=attestations,
        )

        return await self.applications.add(application)
