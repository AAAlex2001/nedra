"""Личный кабинет эксперта."""

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from src.auth.site.dependencies import require_expert
from src.users.models.user import User
from src.users.options import AREAS, CATEGORIES, DIRECTIONS, HAZARD_CLASS_CATEGORY, OBJECTS
from src.users.schemas.expert_certificate import ExpertCertificateRequest
from src.users.site.expert_dependencies import (
    get_add_expert_certificate_usecase,
    get_delete_expert_certificate_usecase,
    get_expert_certificate_scan_usecase,
    get_expert_profile_usecase,
    get_update_expert_certificate_usecase,
    get_update_expert_directions_usecase,
)
from src.users.site.schemas.expert_catalog import ExpertCatalogResponse, HazardClassResponse
from src.users.site.schemas.expert_profile import (
    ExpertProfileResponse,
    UpdateExpertDirectionsRequest,
)
from src.users.site.usecases.add_expert_certificate import AddExpertCertificateUseCase
from src.users.site.usecases.delete_expert_certificate import DeleteExpertCertificateUseCase
from src.users.site.usecases.get_expert_certificate_scan import GetExpertCertificateScanUseCase
from src.users.site.usecases.get_expert_profile import GetExpertProfileUseCase
from src.users.site.usecases.update_expert_certificate import UpdateExpertCertificateUseCase
from src.users.site.usecases.update_expert_directions import UpdateExpertDirectionsUseCase

router = APIRouter(
    prefix="/experts",
    tags=["experts"],
)


@router.get("/catalog")
async def get_catalog() -> ExpertCatalogResponse:
    """Получить справочник аттестации."""

    return ExpertCatalogResponse(
        directions=DIRECTIONS,
        areas=AREAS,
        objects=OBJECTS,
        categories=list(CATEGORIES),
        hazard_classes=[
            HazardClassResponse(
                hazard_class=hazard_class,
                category=category,
            )
            for hazard_class, category in HAZARD_CLASS_CATEGORY.items()
        ],
    )


@router.get("/me")
async def get_expert_profile(
    *,
    user: User = Depends(require_expert),
    usecase: GetExpertProfileUseCase = Depends(get_expert_profile_usecase),
) -> ExpertProfileResponse:
    """Получить свой профиль эксперта."""

    return await usecase.execute(user_id=user.id)


@router.put("/me/directions")
async def update_directions(
    *,
    payload: UpdateExpertDirectionsRequest,
    user: User = Depends(require_expert),
    usecase: UpdateExpertDirectionsUseCase = Depends(get_update_expert_directions_usecase),
) -> ExpertProfileResponse:
    """Изменить направления работы."""

    return await usecase.execute(
        user_id=user.id,
        directions=payload.directions,
    )


@router.post(
    "/me/certificates",
    status_code=201,
)
async def add_certificate(
    *,
    payload: ExpertCertificateRequest,
    user: User = Depends(require_expert),
    usecase: AddExpertCertificateUseCase = Depends(get_add_expert_certificate_usecase),
) -> ExpertProfileResponse:
    """Добавить своё удостоверение."""

    return await usecase.execute(
        user=user,
        payload=payload,
    )


@router.patch("/me/certificates/{certificate_id}")
async def update_certificate(
    *,
    certificate_id: int,
    payload: ExpertCertificateRequest,
    user: User = Depends(require_expert),
    usecase: UpdateExpertCertificateUseCase = Depends(get_update_expert_certificate_usecase),
) -> ExpertProfileResponse:
    """Изменить своё удостоверение."""

    return await usecase.execute(
        user=user,
        certificate_id=certificate_id,
        payload=payload,
    )


@router.delete("/me/certificates/{certificate_id}")
async def delete_certificate(
    *,
    certificate_id: int,
    user: User = Depends(require_expert),
    usecase: DeleteExpertCertificateUseCase = Depends(get_delete_expert_certificate_usecase),
) -> ExpertProfileResponse:
    """Удалить своё удостоверение."""

    return await usecase.execute(
        user=user,
        certificate_id=certificate_id,
    )


@router.get("/me/certificates/{certificate_id}/scan")
async def get_certificate_scan(
    *,
    certificate_id: int,
    user: User = Depends(require_expert),
    usecase: GetExpertCertificateScanUseCase = Depends(get_expert_certificate_scan_usecase),
) -> FileResponse:
    """Открыть скан своего удостоверения."""

    path = await usecase.execute(
        user_id=user.id,
        certificate_id=certificate_id,
    )

    return FileResponse(
        path,
        content_disposition_type="inline",
    )
