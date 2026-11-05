"""Подготовка и подтверждение договора."""

from typing import Literal

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from src.auth.site.dependencies import get_current_user, require_customer
from src.documents.http_response import document_response
from src.expertise.schemas.expertise import ExpertiseResponse
from src.expertise.schemas.expertise_contract import ExpertiseContractResponse
from src.expertise.site.contract_dependencies import (
    get_confirm_expertise_contract_usecase,
    get_expertise_contract_document_usecase,
    get_expertise_contract_usecase,
)
from src.expertise.site.usecases.confirm_contract import ConfirmExpertiseContractUseCase
from src.expertise.site.usecases.get_contract_document import GetExpertiseContractDocumentUseCase
from src.expertise.site.usecases.get_expertise_contract import GetExpertiseContractUseCase
from src.users.models.user import User

router = APIRouter(
    prefix="/expertises",
    tags=["expertise"],
)


@router.post("/{expertise_id}/confirm")
async def confirm_expertise_contract(
    *,
    expertise_id: int,
    user: User = Depends(require_customer),
    usecase: ConfirmExpertiseContractUseCase = Depends(get_confirm_expertise_contract_usecase),
) -> ExpertiseResponse:
    """Подтвердить договор и соглашение."""

    return await usecase.execute(
        expertise_id=expertise_id,
        user=user,
    )


@router.get("/{expertise_id}/signing/{kind}")
async def get_expertise_contract_document(
    *,
    expertise_id: int,
    kind: Literal["contract", "nda"],
    user: User = Depends(get_current_user),
    usecase: GetExpertiseContractDocumentUseCase = Depends(get_expertise_contract_document_usecase),
) -> Response:
    """Скачать договор или соглашение."""

    document = await usecase.execute(
        expertise_id=expertise_id,
        document_kind=kind,
        user=user,
    )

    return document_response(document=document)


@router.get("/{expertise_id}/contract")
async def get_expertise_contract(
    *,
    expertise_id: int,
    user: User = Depends(get_current_user),
    usecase: GetExpertiseContractUseCase = Depends(get_expertise_contract_usecase),
) -> ExpertiseContractResponse | None:
    """Получить сведения о договоре."""

    return await usecase.execute(
        expertise_id=expertise_id,
        user=user,
    )
