"""Документы и замечания."""

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from src.auth.site.dependencies import get_current_user
from src.expertise.site.documents_dependencies import (
    get_expertise_document_usecase,
    list_expertise_documents_usecase,
    list_expertise_remarks_usecase,
)
from src.expertise.site.schemas.expertise_documents import (
    ExpertiseDocumentResponse,
    ExpertiseRemarkResponse,
)
from src.expertise.site.usecases.get_expertise_document import GetExpertiseDocumentUseCase
from src.expertise.site.usecases.list_expertise_documents import ListExpertiseDocumentsUseCase
from src.expertise.site.usecases.list_expertise_remarks import ListExpertiseRemarksUseCase
from src.users.models.user import User

router = APIRouter(
    prefix="/expertises",
    tags=["expertise"],
)


@router.get("/{expertise_id}/documents/{document_id}")
async def get_expertise_document(
    *,
    expertise_id: int,
    document_id: int,
    user: User = Depends(get_current_user),
    usecase: GetExpertiseDocumentUseCase = Depends(get_expertise_document_usecase),
) -> FileResponse:
    """Скачать документ."""

    path, filename = await usecase.execute(
        expertise_id=expertise_id,
        document_id=document_id,
        user=user,
    )
    return FileResponse(path, filename=filename)


@router.get("/{expertise_id}/documents")
async def list_expertise_documents(
    *,
    expertise_id: int,
    user: User = Depends(get_current_user),
    usecase: ListExpertiseDocumentsUseCase = Depends(list_expertise_documents_usecase),
) -> list[ExpertiseDocumentResponse]:
    """Получить документы экспертизы."""

    return await usecase.execute(
        expertise_id=expertise_id,
        user=user,
    )


@router.get("/{expertise_id}/remarks")
async def list_expertise_remarks(
    *,
    expertise_id: int,
    user: User = Depends(get_current_user),
    usecase: ListExpertiseRemarksUseCase = Depends(list_expertise_remarks_usecase),
) -> list[ExpertiseRemarkResponse]:
    """Получить замечания эксперта."""

    return await usecase.execute(
        expertise_id=expertise_id,
        user=user,
    )
