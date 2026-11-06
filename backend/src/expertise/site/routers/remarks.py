"""Замечания и исправленные документы."""

from fastapi import APIRouter, Depends, File, Form, UploadFile

from src.auth.site.dependencies.authentication import require_customer, require_expert
from src.expertise.schemas.expertise import ExpertiseResponse
from src.expertise.site.dependencies.remarks import (
    get_resubmit_documents_expertise_usecase,
    get_send_remarks_expertise_usecase,
)
from src.expertise.site.usecases.resubmit_documents import (
    ResubmitExpertiseDocumentsUseCase,
)
from src.expertise.site.usecases.send_remarks import SendExpertiseRemarksUseCase
from src.users.models.user import User

router = APIRouter(
    prefix="/expertises",
    tags=["expertise"],
)


@router.post("/{expertise_id}/remarks")
async def send_remarks(
    *,
    expertise_id: int,
    user: User = Depends(require_expert),
    usecase: SendExpertiseRemarksUseCase = Depends(get_send_remarks_expertise_usecase),
    files: list[UploadFile] = File(default=[]),
    text: str | None = Form(default=None),
) -> ExpertiseResponse:
    """Отправить замечания заказчику."""

    return await usecase.execute(
        expertise_id=expertise_id,
        user=user,
        files=files,
        text=text,
    )


@router.post("/{expertise_id}/revision")
async def resubmit_documents(
    *,
    expertise_id: int,
    user: User = Depends(require_customer),
    usecase: ResubmitExpertiseDocumentsUseCase = Depends(get_resubmit_documents_expertise_usecase),
    files: list[UploadFile] = File(default=[]),
    text: str | None = Form(default=None),
) -> ExpertiseResponse:
    """Отправить исправленные документы."""

    return await usecase.execute(
        expertise_id=expertise_id,
        user=user,
        files=files,
        text=text,
    )
