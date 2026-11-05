"""Подготовка, передача и приёмка заключения."""

from fastapi import APIRouter, Depends, File, Form, UploadFile

from src.auth.site.dependencies import require_customer, require_expert
from src.expertise.enums import ExpertiseResult
from src.expertise.schemas.expertise import ExpertiseResponse
from src.expertise.site.conclusion_dependencies import (
    get_accept_work_expertise_usecase,
    get_mark_conclusion_ready_expertise_usecase,
    get_send_conclusion_expertise_usecase,
)
from src.expertise.site.usecases.accept_work import AcceptExpertiseWorkUseCase
from src.expertise.site.usecases.mark_conclusion_ready import MarkExpertiseConclusionReadyUseCase
from src.expertise.site.usecases.send_conclusion import SendExpertiseConclusionUseCase
from src.users.models.user import User

router = APIRouter(
    prefix="/expertises",
    tags=["expertise"],
)


@router.post("/{expertise_id}/conclusion-ready")
async def mark_conclusion_ready(
    *,
    expertise_id: int,
    user: User = Depends(require_expert),
    usecase: MarkExpertiseConclusionReadyUseCase = Depends(
        get_mark_conclusion_ready_expertise_usecase
    ),
) -> ExpertiseResponse:
    """Сообщить о готовности заключения."""

    return await usecase.execute(
        expertise_id=expertise_id,
        user=user,
    )


@router.post("/{expertise_id}/accept-work")
async def accept_work(
    *,
    expertise_id: int,
    user: User = Depends(require_customer),
    usecase: AcceptExpertiseWorkUseCase = Depends(get_accept_work_expertise_usecase),
) -> ExpertiseResponse:
    """Принять выполненную работу."""

    return await usecase.execute(
        expertise_id=expertise_id,
        user=user,
    )


@router.post("/{expertise_id}/conclusion")
async def send_conclusion(
    *,
    expertise_id: int,
    user: User = Depends(require_expert),
    usecase: SendExpertiseConclusionUseCase = Depends(get_send_conclusion_expertise_usecase),
    files: list[UploadFile] = File(default=[]),
    result: ExpertiseResult | None = Form(default=None),
) -> ExpertiseResponse:
    """Передать заключение заказчику."""

    return await usecase.execute(
        expertise_id=expertise_id,
        user=user,
        files=files,
        result=result,
    )
