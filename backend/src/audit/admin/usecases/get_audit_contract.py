"""Просмотр условий договора."""

from src.audit.exceptions import AuditNotFoundError
from src.audit.repositories.audits import AuditRepository
from src.audit.schemas.audit_contract import AuditContractResponse
from src.contracts.repositories.contracts import ContractRepository


class GetAdminAuditContractUseCase:
    """Вид и подтверждение договора."""

    def __init__(
        self,
        *,
        audits: AuditRepository,
        contracts: ContractRepository,
    ) -> None:
        """Права доступа и договоры."""

        self.audits = audits
        self.contracts = contracts

    async def execute(self, *, audit_id: int) -> AuditContractResponse | None:
        """Получить сведения о договоре."""

        audit = await self.audits.get_by_id(audit_id=audit_id)

        if audit is None:
            raise AuditNotFoundError()

        contract = await self.contracts.get_for_audit(audit_id=audit_id)

        if contract is None:
            return None

        return AuditContractResponse.from_model(contract=contract)
