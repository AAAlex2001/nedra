"""Удаление работы администратором."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.exceptions import AuditNotFoundError, AuditStateError
from src.audit.repositories.audit_documents import AuditDocumentRepository
from src.audit.repositories.audit_payments import AuditPaymentRepository
from src.audit.repositories.audits import AuditRepository
from src.billing.repositories.invoices import InvoiceRepository
from src.core.file_storage import FileStorage


class DeleteAuditUseCase:
    """Удаление работы без платёжной истории."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        audits: AuditRepository,
        documents: AuditDocumentRepository,
        payments: AuditPaymentRepository,
        invoices: InvoiceRepository,
        storage: FileStorage,
    ) -> None:
        """Работа, платёжная история и файлы."""

        self.session = session
        self.audits = audits
        self.documents = documents
        self.payments = payments
        self.invoices = invoices
        self.storage = storage

    async def execute(self, *, audit_id: int) -> None:
        """Удалить работу и её файлы."""

        audit = await self.audits.get_for_update(audit_id=audit_id)
        if audit is None:
            raise AuditNotFoundError()

        if await self.payments.has_payments(audit_id=audit_id):
            raise AuditStateError("Нельзя удалить работу с платёжной историей")

        if await self.invoices.has_for_audit(audit_id=audit_id):
            raise AuditStateError("Нельзя удалить работу с выставленными счетами")

        documents = await self.documents.list_for_audit(audit_id=audit_id)
        await self.audits.delete(audit=audit)
        await self.session.commit()

        for document in documents:
            await self.storage.remove_failed_upload(relative_path=document.file_path)
