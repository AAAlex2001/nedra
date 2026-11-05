"""Загрузка приложения к публикации."""

from src.articles.admin.schemas.upload import UploadedFileResponse, UploadFileRequest
from src.articles.options import DOCUMENT_MAX_SIZE_BYTES, DOCUMENT_TYPES
from src.core.file_storage import FileStorage


class UploadArticleDocumentUseCase:
    """Документы для скачивания."""

    def __init__(self, *, storage: FileStorage) -> None:
        """Публичное хранилище."""

        self.storage = storage

    async def execute(self, *, payload: UploadFileRequest) -> UploadedFileResponse:
        """Проверить и сохранить документ."""

        stored = await self.storage.save(
            file=payload.file,
            folder="articles/documents",
            max_size_bytes=DOCUMENT_MAX_SIZE_BYTES,
            allowed_types=DOCUMENT_TYPES,
            types_label="PDF, Word и Excel",
        )

        return UploadedFileResponse(url=f"/media/{stored.path}")
