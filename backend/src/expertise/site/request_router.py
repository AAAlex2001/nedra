"""Подача и просмотр заявок."""

from fastapi import APIRouter, Depends, File, UploadFile

from src.auth.site.dependencies import get_current_user, require_customer, require_expert
from src.expertise.schemas.expertise import ExpertiseResponse
from src.expertise.schemas.expertise_participants import ExpertiseParticipantsResponse
from src.expertise.site.request_dependencies import (
    get_accept_expertise_usecase,
    get_create_expertise_usecase,
    get_expertise_participants_usecase,
    get_expertise_usecase,
    get_list_expertises_usecase,
    parse_expertise_form,
)
from src.expertise.site.schemas.accept_expertise import AcceptExpertiseRequest
from src.expertise.site.schemas.create_expertise import CreateExpertiseRequest
from src.expertise.site.schemas.list_expertises import ExpertiseListItemResponse
from src.expertise.site.usecases.accept_expertise import AcceptExpertiseUseCase
from src.expertise.site.usecases.create_expertise import CreateExpertiseUseCase
from src.expertise.site.usecases.get_expertise import GetExpertiseUseCase
from src.expertise.site.usecases.get_expertise_participants import GetExpertiseParticipantsUseCase
from src.expertise.site.usecases.list_expertises import ListExpertisesUseCase
from src.users.models.user import User

router = APIRouter(
    prefix="/expertises",
    tags=["expertise"],
)


@router.get("/my")
async def list_my_expertises(
    *,
    user: User = Depends(require_customer),
    usecase: ListExpertisesUseCase = Depends(get_list_expertises_usecase),
) -> list[ExpertiseListItemResponse]:
    """Получить свои работы."""

    return await usecase.execute(
        user=user,
        scope="my",
    )


@router.get("/incoming")
async def list_incoming_expertises(
    *,
    user: User = Depends(require_expert),
    usecase: ListExpertisesUseCase = Depends(get_list_expertises_usecase),
    object_code: str | None = None,
    area_code: str | None = None,
) -> list[ExpertiseListItemResponse]:
    """Получить входящие работы."""

    return await usecase.execute(
        user=user,
        scope="incoming",
        object_code=object_code,
        area_code=area_code,
    )


@router.get("/assigned")
async def list_assigned_expertises(
    *,
    user: User = Depends(require_expert),
    usecase: ListExpertisesUseCase = Depends(get_list_expertises_usecase),
) -> list[ExpertiseListItemResponse]:
    """Получить назначенные работы."""

    return await usecase.execute(
        user=user,
        scope="assigned",
    )


@router.post("", status_code=201)
async def create_expertise(
    *,
    payload: CreateExpertiseRequest = Depends(parse_expertise_form),
    files: list[UploadFile] = File(default=[]),
    company_card: UploadFile | None = File(default=None),
    user: User = Depends(require_customer),
    usecase: CreateExpertiseUseCase = Depends(get_create_expertise_usecase),
) -> ExpertiseResponse:
    """Подать документацию на экспертизу."""

    return await usecase.execute(
        user=user,
        payload=payload,
        files=files,
        company_card=company_card,
    )


@router.get("/{expertise_id}")
async def get_expertise(
    *,
    expertise_id: int,
    user: User = Depends(get_current_user),
    usecase: GetExpertiseUseCase = Depends(get_expertise_usecase),
) -> ExpertiseResponse:
    """Открыть карточку услуги."""

    return await usecase.execute(
        expertise_id=expertise_id,
        user=user,
    )


@router.post("/{expertise_id}/accept")
async def accept_expertise(
    *,
    expertise_id: int,
    payload: AcceptExpertiseRequest | None = None,
    user: User = Depends(require_expert),
    usecase: AcceptExpertiseUseCase = Depends(get_accept_expertise_usecase),
) -> ExpertiseResponse:
    """Принять заявку в работу."""

    return await usecase.execute(
        expertise_id=expertise_id,
        user=user,
        contract_kind=payload.contract_kind if payload else None,
    )


@router.get("/{expertise_id}/participants")
async def get_expertise_participants(
    *,
    expertise_id: int,
    user: User = Depends(get_current_user),
    usecase: GetExpertiseParticipantsUseCase = Depends(get_expertise_participants_usecase),
) -> ExpertiseParticipantsResponse:
    """Получить участников и реквизиты."""

    return await usecase.execute(
        expertise_id=expertise_id,
        user=user,
    )
