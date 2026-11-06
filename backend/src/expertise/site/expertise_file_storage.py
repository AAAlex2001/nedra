"""Хранение файлов экспертизы."""

import logging
from dataclasses import dataclass

from fastapi import UploadFile

from src.core.file_storage import FileStorage
from src.core.stored_file import StoredFile
from src.expertise.models.expertise_document import ExpertiseDocument
from src.expertise.options import (
    DOCUMENT_TYPES,
    DOCUMENT_TYPES_LABEL,
    DOCUMENTATION_MAX_SIZE_BYTES,
    DOCUMENTS_FOLDER,
)


@dataclass(
    frozen=True,
    kw_only=True,
)
class ExpertiseAttachment:
    """Загружаемый документ экспертизы."""

    file: UploadFile  # Загруженный файл.
    kind: str  # Назначение документа.


@dataclass(frozen=True)
class SavedExpertiseDocument:
    """Сохранённое приложение к экспертизе."""

    file: StoredFile  # Файл в хранилище.
    kind: str  # Назначение документа.

    def to_model(
        self,
        *,
        expertise_id: int,
        uploaded_by: int,
        remark_id: int | None = None,
    ) -> ExpertiseDocument:
        """Подготовить запись сохранённого документа."""

        return ExpertiseDocument(
            expertise_id=expertise_id,
            uploaded_by=uploaded_by,
            remark_id=remark_id,
            kind=self.kind,
            file_path=self.file.path,
            original_name=self.file.original_name,
            size=self.file.size,
            content_type=self.file.content_type,
        )


class ExpertiseFileStorage:
    """Загрузка и удаление приложений экспертизы."""

    def __init__(self, *, storage: FileStorage) -> None:
        """Хранилище документов."""

        self.storage = storage

    async def save_all(
        self, *, attachments: list[ExpertiseAttachment]
    ) -> list[SavedExpertiseDocument]:
        """Сохранить приложения заявки."""

        documents = []

        try:
            for attachment in attachments:
                saved_file = await self.storage.save(
                    file=attachment.file,
                    folder=DOCUMENTS_FOLDER,
                    max_size_bytes=DOCUMENTATION_MAX_SIZE_BYTES,
                    allowed_types=DOCUMENT_TYPES,
                    types_label=DOCUMENT_TYPES_LABEL,
                )
                documents.append(
                    SavedExpertiseDocument(
                        file=saved_file,
                        kind=attachment.kind,
                    )
                )
        except Exception:
            await self.remove_all(documents=documents)
            raise

        return documents

    async def remove_all(self, *, documents: list[SavedExpertiseDocument]) -> None:
        """Удалить приложения после ошибки."""

        for document in documents:
            try:
                await self.storage.remove(relative_path=document.file.path)
            except OSError:
                logging.getLogger(__name__).error(
                    "Не удалось удалить файл: %s",
                    document.file.path,
                )
