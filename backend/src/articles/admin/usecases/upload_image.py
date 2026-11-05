"""Загрузка изображения публикации."""

from src.articles.admin.schemas.upload import UploadedFileResponse, UploadFileRequest
from src.articles.options import IMAGE_MAX_SIZE_BYTES, IMAGE_TYPES
from src.core.file_storage import FileStorage


class UploadArticleImageUseCase:
    """Обложки и изображения для текста."""

    def __init__(self, *, storage: FileStorage) -> None:
        """Публичное хранилище."""

        self.storage = storage

    async def execute(self, *, payload: UploadFileRequest) -> UploadedFileResponse:
        """Проверить и сохранить изображение."""

        stored = await self.storage.save(
            file=payload.file,
            folder="articles",
            max_size_bytes=IMAGE_MAX_SIZE_BYTES,
            allowed_types=IMAGE_TYPES,
            types_label="JPEG, PNG и WebP",
        )

        return UploadedFileResponse(url=f"/media/{stored.path}")
