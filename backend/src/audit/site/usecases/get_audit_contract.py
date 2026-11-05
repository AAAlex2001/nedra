"""Просмотр условий договора."""

from src.audit.schemas.audit_contract import AuditContractResponse
from src.audit.site.audit_access import AuditAccess
from src.contracts.repositories.contracts import ContractRepository
from src.users.models.user import User


class GetAuditContractUseCase:
    """Вид и подтверждение договора."""

    def __init__(
        self,
        *,
        access: AuditAccess,
        contracts: ContractRepository,
    ) -> None:
        """Права доступа и договоры."""

        self.access = access
        self.contracts = contracts

    async def execute(
        self,
        *,
        audit_id: int,
        user: User,
    ) -> AuditContractResponse | None:
        """Получить сведения о договоре."""

        await self.access.get_visible(
            audit_id=audit_id,
            user=user,
        )
        contract = await self.contracts.get_for_audit(audit_id=audit_id)

        if contract is None:
            return None

        return AuditContractResponse.from_model(contract=contract)
