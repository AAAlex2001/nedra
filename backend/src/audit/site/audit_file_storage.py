"""Хранение файлов аудита."""

import logging
from dataclasses import dataclass

from src.audit.options import DOCUMENTS_FOLDER, FILE_MAX_SIZE_BYTES, FILE_TYPES, FILE_TYPES_LABEL
from src.audit.site.audit_upload_files import AuditAttachedFile
from src.core.file_storage import FileStorage
from src.core.stored_file import StoredFile


@dataclass(frozen=True)
class SavedAuditDocument:
    """Сохранённое приложение к аудиту."""

    file: StoredFile  # Файл в хранилище.
    kind: str  # Назначение документа.
    item_number: int | None  # Номер пункта перечня.


class AuditFileStorage:
    """Загрузка и удаление приложений аудита."""

    def __init__(self, *, storage: FileStorage) -> None:
        """Хранилище документов."""

        self.storage = storage

    async def save_all(self, *, attachments: list[AuditAttachedFile]) -> list[SavedAuditDocument]:
        """Сохранить приложения заявки."""

        documents = []

        try:
            for attachment in attachments:
                saved_file = await self.storage.save(
                    file=attachment.file,
                    folder=DOCUMENTS_FOLDER,
                    max_size_bytes=FILE_MAX_SIZE_BYTES,
                    allowed_types=FILE_TYPES,
                    types_label=FILE_TYPES_LABEL,
                )
                documents.append(
                    SavedAuditDocument(
                        file=saved_file,
                        kind=attachment.kind,
                        item_number=attachment.item_number,
                    )
                )
        except Exception:
            await self.remove_all(documents=documents)
            raise

        return documents

    async def remove_all(self, *, documents: list[SavedAuditDocument]) -> None:
        """Удалить приложения после ошибки."""

        for document in documents:
            try:
                await self.storage.remove(relative_path=document.file.path)
            except OSError:
                logging.getLogger(__name__).error(
                    "Не удалось удалить файл: %s",
                    document.file.path,
                )
