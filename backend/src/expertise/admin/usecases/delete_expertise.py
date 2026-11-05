"""Удаление работы администратором."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.billing.repositories.invoices import InvoiceRepository
from src.core.file_storage import FileStorage
from src.expertise.exceptions import ExpertiseNotFoundError, ExpertiseStateError
from src.expertise.repositories.expertise_documents import ExpertiseDocumentRepository
from src.expertise.repositories.expertise_payments import ExpertisePaymentRepository
from src.expertise.repositories.expertises import ExpertiseRepository


class DeleteExpertiseUseCase:
    """Удаление работы без платёжной истории."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        expertises: ExpertiseRepository,
        documents: ExpertiseDocumentRepository,
        payments: ExpertisePaymentRepository,
        invoices: InvoiceRepository,
        storage: FileStorage,
    ) -> None:
        """Работа, платёжная история и файлы."""

        self.session = session
        self.expertises = expertises
        self.documents = documents
        self.payments = payments
        self.invoices = invoices
        self.storage = storage

    async def execute(self, *, expertise_id: int) -> None:
        """Удалить работу и её файлы."""

        expertise = await self.expertises.get_for_update(expertise_id=expertise_id)
        if expertise is None:
            raise ExpertiseNotFoundError()

        if await self.payments.has_payments(expertise_id=expertise_id):
            raise ExpertiseStateError("Нельзя удалить работу с платёжной историей")

        if await self.invoices.has_for_expertise(expertise_id=expertise_id):
            raise ExpertiseStateError("Нельзя удалить работу с выставленными счетами")

        documents = await self.documents.list_for_expertise(expertise_id=expertise_id)
        await self.expertises.delete(expertise=expertise)
        await self.session.commit()

        for document in documents:
            await self.storage.remove_failed_upload(relative_path=document.file_path)
