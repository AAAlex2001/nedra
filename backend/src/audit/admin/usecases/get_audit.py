"""Открытие карточки аудита."""

from src.audit.exceptions import AuditNotFoundError
from src.audit.repositories.audits import AuditRepository
from src.audit.schemas.audit import AuditResponse


class GetAdminAuditUseCase:
    """Карточка для администратора."""

    def __init__(self, *, audits: AuditRepository) -> None:
        """Права доступа и данные карточки."""

        self.audits = audits

    async def execute(self, *, audit_id: int) -> AuditResponse:
        """Открыть карточку."""

        audit = await self.audits.get_by_id(audit_id=audit_id)

        if audit is None:
            raise AuditNotFoundError()

        return AuditResponse.from_model(audit=audit)
