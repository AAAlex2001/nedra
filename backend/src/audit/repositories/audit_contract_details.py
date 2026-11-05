"""Чтение данных для договора аудита."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.audit_contract_details import AuditContractDetails
from src.audit.models.audit import Audit
from src.audit.models.audit_application import AuditApplication
from src.audit.models.audit_company import AuditCompany
from src.contracts.models.contract import Contract


class AuditContractDetailsRepository:
    """Условия и реквизиты договора."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def get(self, *, audit_id: int) -> AuditContractDetails | None:
        """Получить данные для договора."""

        audit = await self.session.get(Audit, audit_id)
        if audit is None:
            return None

        contract_statement = select(Contract).where(Contract.audit_id == audit_id)
        contract = await self.session.scalar(contract_statement)
        company = await self.session.get(AuditCompany, audit_id)
        application = await self.session.get(AuditApplication, audit_id)

        return AuditContractDetails(
            audit=audit,
            contract=contract,
            company=company,
            application=application,
        )
