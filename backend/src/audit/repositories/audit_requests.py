"""Сохранение заявки и её приложений."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.models.audit import Audit
from src.audit.models.audit_application import AuditApplication
from src.audit.models.audit_company import AuditCompany
from src.audit.models.audit_document import AuditDocument


class AuditRequestRepository:
    """Записи одной заявки."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def add(
        self,
        *,
        audit: Audit,
        application: AuditApplication,
        company: AuditCompany,
        documents: list[AuditDocument],
    ) -> None:
        """Добавить заявку, реквизиты и документы."""

        self.session.add(audit)
        await self.session.flush()

        application.audit_id = audit.id
        company.audit_id = audit.id
        self.session.add_all([application, company])

        for document in documents:
            document.audit_id = audit.id

        self.session.add_all(documents)
        await self.session.flush()
