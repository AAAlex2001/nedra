"""Реквизиты заказчика аудита."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.models.audit_company import AuditCompany


class AuditCustomerRepository:
    """Чтение реквизитов организации или ИП."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def get_company(self, *, audit_id: int) -> AuditCompany | None:
        """Получить сохранённые реквизиты."""

        return await self.session.get(AuditCompany, audit_id)
