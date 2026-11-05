"""Список актов заказчика."""

from src.audit.enums import AuditStatus
from src.audit.repositories.audit_applications import AuditApplicationRepository
from src.audit.repositories.audits import AuditRepository
from src.billing.schemas.act import ActResponse
from src.expertise.enums import ExpertiseStatus
from src.expertise.repositories.expertises import ExpertiseRepository


class ListActsUseCase:
    """Акты по принятым работам двух услуг."""

    def __init__(
        self,
        *,
        audits: AuditRepository,
        applications: AuditApplicationRepository,
        expertises: ExpertiseRepository,
    ) -> None:
        """Аудиты, объекты и экспертизы."""

        self.audits = audits
        self.applications = applications
        self.expertises = expertises

    async def execute(self, *, user_id: int) -> list[ActResponse]:
        """Получить акты заказчика."""

        audits = await self.audits.list_for_customer(user_id=user_id)
        expertises = await self.expertises.list_for_customer(user_id=user_id)
        applications = await self.applications.list_by_audit_ids(
            audit_ids={audit.id for audit in audits}
        )
        acts = []

        for audit in audits:
            if audit.status != AuditStatus.ACCEPTED:
                continue

            signed_at = audit.accepted_at or audit.created_at
            application = applications.get(audit.id)
            acts.append(
                ActResponse(
                    audit_id=audit.id,
                    expertise_id=None,
                    number=f"БА-{signed_at.year}-{audit.id:04d}",
                    amount=audit.agreed_price,
                    subject=application.object_name
                    if application is not None and application.object_name
                    else "Аудит СУПБ",
                    signed_at=signed_at,
                )
            )

        for expertise in expertises:
            if expertise.status != ExpertiseStatus.ACCEPTED:
                continue

            signed_at = expertise.accepted_at or expertise.created_at
            acts.append(
                ActResponse(
                    audit_id=None,
                    expertise_id=expertise.id,
                    number=f"БЭ-{signed_at.year}-{expertise.id:04d}",
                    amount=expertise.price,
                    subject=expertise.object_name or "Экспертиза промышленной безопасности",
                    signed_at=signed_at,
                )
            )

        return sorted(
            acts,
            key=lambda act: (act.signed_at, act.number),
            reverse=True,
        )
