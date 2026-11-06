"""Зависимости публикаций."""

from fastapi import Depends

from src.articles.admin.usecases.upload_document import UploadArticleDocumentUseCase
from src.articles.admin.usecases.upload_image import UploadArticleImageUseCase
from src.core.file_storage import FileStorage
from src.core.settings import Settings, get_settings


def get_upload_image_usecase(
    *, settings: Settings = Depends(get_settings)
) -> UploadArticleImageUseCase:
    """Загрузка изображения."""

    return UploadArticleImageUseCase(
        storage=FileStorage(directory=settings.media_dir),
    )


def get_upload_document_usecase(
    *, settings: Settings = Depends(get_settings)
) -> UploadArticleDocumentUseCase:
    """Загрузка документа."""

    return UploadArticleDocumentUseCase(
        storage=FileStorage(directory=settings.media_dir),
    )
