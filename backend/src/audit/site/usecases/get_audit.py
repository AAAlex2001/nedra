"""Открытие карточки аудита."""

from src.audit.schemas.audit import AuditResponse
from src.audit.site.audit_access import AuditAccess
from src.users.models.user import User


class GetAuditUseCase:
    """Карточка для участника услуги."""

    def __init__(self, *, access: AuditAccess) -> None:
        """Права доступа и данные карточки."""

        self.access = access

    async def execute(
        self,
        *,
        audit_id: int,
        user: User,
    ) -> AuditResponse:
        """Открыть карточку."""

        audit = await self.access.get_visible(
            audit_id=audit_id,
            user=user,
        )
        return AuditResponse.from_model(audit=audit)
