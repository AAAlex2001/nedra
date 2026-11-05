"""Приложения к сообщению об оплате."""

from fastapi import UploadFile

from src.audit.models.audit_document import AuditDocument
from src.audit.repositories.audit_documents import AuditDocumentRepository
from src.billing.models.invoice import Invoice
from src.billing.options import (
    DOCUMENT_MAX_SIZE_BYTES,
    DOCUMENT_TYPES,
    DOCUMENT_TYPES_LABEL,
    DOCUMENTS_FOLDER,
)
from src.core.file_storage import FileStorage
from src.core.stored_file import StoredFile
from src.expertise.models.expertise_document import ExpertiseDocument
from src.expertise.repositories.expertise_documents import ExpertiseDocumentRepository


class InvoiceAttachments:
    """Платёжные документы в файлах соответствующей работы."""

    def __init__(
        self,
        *,
        storage: FileStorage,
        audit_documents: AuditDocumentRepository,
        expertise_documents: ExpertiseDocumentRepository,
    ) -> None:
        """Хранилище и документы двух услуг."""

        self.storage = storage
        self.audit_documents = audit_documents
        self.expertise_documents = expertise_documents

    async def save(
        self,
        *,
        invoice: Invoice,
        file: UploadFile,
        kind: str,
        user_id: int,
    ) -> StoredFile:
        """Сохранить платёжный документ работы."""

        stored_file = await self.storage.save(
            file=file,
            folder=DOCUMENTS_FOLDER,
            max_size_bytes=DOCUMENT_MAX_SIZE_BYTES,
            allowed_types=DOCUMENT_TYPES,
            types_label=DOCUMENT_TYPES_LABEL,
        )
        try:
            if invoice.audit_id is not None:
                document = AuditDocument(
                    audit_id=invoice.audit_id,
                    uploaded_by=user_id,
                    kind=kind,
                    file_path=stored_file.path,
                    original_name=stored_file.original_name,
                    size=stored_file.size,
                    content_type=stored_file.content_type,
                )
                await self.audit_documents.add_many(documents=[document])
            else:
                document = ExpertiseDocument(
                    expertise_id=invoice.expertise_id,
                    uploaded_by=user_id,
                    kind=kind,
                    file_path=stored_file.path,
                    original_name=stored_file.original_name,
                    size=stored_file.size,
                    content_type=stored_file.content_type,
                )
                await self.expertise_documents.add_many(documents=[document])
        except Exception:
            await self.remove(file=stored_file)
            raise

        return stored_file

    async def remove(self, *, file: StoredFile) -> None:
        """Удалить файл несохранённого сообщения."""

        await self.storage.remove_failed_upload(relative_path=file.path)
