"""Договоры по заявкам."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.contracts.models.contract import Contract


class ContractRepository:
    """Чтение и сохранение договоров."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def get_for_audit(self, *, audit_id: int) -> Contract | None:
        """Найти договор аудита."""

        return await self.session.scalar(select(Contract).where(Contract.audit_id == audit_id))

    async def get_for_expertise(self, *, expertise_id: int) -> Contract | None:
        """Найти договор экспертизы."""

        return await self.session.scalar(
            select(Contract).where(Contract.expertise_id == expertise_id)
        )

    async def save(self, *, contract: Contract) -> None:
        """Сохранить условия договора."""

        self.session.add(contract)
        await self.session.flush()
