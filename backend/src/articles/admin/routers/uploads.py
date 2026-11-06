"""Загрузка файлов публикаций."""

from fastapi import APIRouter, Depends, UploadFile

from src.articles.admin.dependencies.uploads import (
    get_upload_document_usecase,
    get_upload_image_usecase,
)
from src.articles.admin.schemas.upload import UploadedFileResponse, UploadFileRequest
from src.articles.admin.usecases.upload_document import UploadArticleDocumentUseCase
from src.articles.admin.usecases.upload_image import UploadArticleImageUseCase
from src.auth.admin.access import require_admin

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


@router.post("/uploads", status_code=201)
async def upload_image(
    *,
    file: UploadFile,
    usecase: UploadArticleImageUseCase = Depends(get_upload_image_usecase),
) -> UploadedFileResponse:
    """Загрузить изображение."""

    payload = UploadFileRequest(file=file)

    return await usecase.execute(payload=payload)


@router.post("/uploads/documents", status_code=201)
async def upload_document(
    *,
    file: UploadFile,
    usecase: UploadArticleDocumentUseCase = Depends(get_upload_document_usecase),
) -> UploadedFileResponse:
    """Загрузить документ."""

    payload = UploadFileRequest(file=file)

    return await usecase.execute(payload=payload)
