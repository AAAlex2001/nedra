"""Подача заявки кандидата."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.commission.models.commission_application import CommissionApplication
from src.commission.repositories.commission_applications import (
    CommissionApplicationRepository,
)
from src.commission.schemas.commission_application import (
    CommissionApplicationResponse,
    CreateCommissionApplicationRequest,
)
from src.commission.site.commission_letters import CommissionLetters
from src.users.attestation_validation import validate_certificate


class CreateCommissionApplicationUseCase:
    """Заявка в конкурсную комиссию."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        applications: CommissionApplicationRepository,
        letters: CommissionLetters,
    ) -> None:
        """Зависимости подачи заявки."""

        self.session = session
        self.applications = applications
        self.letters = letters

    async def execute(
        self, *, payload: CreateCommissionApplicationRequest
    ) -> CommissionApplicationResponse:
        """Подать заявку кандидата."""

        for attestation in payload.attestations:
            validate_certificate(
                area_code=attestation.area_code,
                object_code=attestation.object_code,
                category=attestation.category,
            )

        application = CommissionApplication(
            full_name=payload.full_name,
            phone=payload.phone,
            email=str(payload.email),
            attestations=[attestation.model_dump() for attestation in payload.attestations],
        )
        await self.applications.add(application=application)
        response = CommissionApplicationResponse.from_model(application=application)
        await self.session.commit()
        await self.letters.send_created(application=application)

        return response
