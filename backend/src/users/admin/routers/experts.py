"""Управление экспертами."""

from fastapi import APIRouter, Depends

from src.auth.admin.access import require_admin
from src.users.admin.dependencies.certificates import (
    get_add_expert_certificate_usecase,
    get_delete_expert_certificate_usecase,
    get_update_expert_certificate_usecase,
)
from src.users.admin.dependencies.experts import (
    get_delete_expert_usecase,
    get_list_experts_usecase,
    get_update_expert_usecase,
)
from src.users.admin.schemas.expert import ExpertResponse, UpdateExpertRequest
from src.users.admin.usecases.add_expert_certificate import AddExpertCertificateUseCase
from src.users.admin.usecases.delete_expert import DeleteExpertUseCase
from src.users.admin.usecases.delete_expert_certificate import (
    DeleteExpertCertificateUseCase,
)
from src.users.admin.usecases.list_experts import ListExpertsUseCase
from src.users.admin.usecases.update_expert import UpdateExpertUseCase
from src.users.admin.usecases.update_expert_certificate import (
    UpdateExpertCertificateUseCase,
)
from src.users.schemas.expert_certificate import ExpertCertificateRequest

router = APIRouter(
    prefix="/admin/experts",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


@router.get("")
async def list_experts(
    *,
    usecase: ListExpertsUseCase = Depends(get_list_experts_usecase),
) -> list[ExpertResponse]:
    """Получить список экспертов."""

    return await usecase.execute()


@router.patch("/{user_id}")
async def update_expert(
    *,
    user_id: int,
    payload: UpdateExpertRequest,
    usecase: UpdateExpertUseCase = Depends(get_update_expert_usecase),
) -> ExpertResponse:
    """Изменить профиль эксперта."""

    return await usecase.execute(
        user_id=user_id,
        payload=payload,
    )


@router.delete("/{user_id}", status_code=204)
async def delete_expert(
    *,
    user_id: int,
    usecase: DeleteExpertUseCase = Depends(get_delete_expert_usecase),
) -> None:
    """Удалить аккаунт эксперта."""

    await usecase.execute(user_id=user_id)


@router.post("/{user_id}/certificates", status_code=204)
async def add_expert_certificate(
    *,
    user_id: int,
    payload: ExpertCertificateRequest,
    usecase: AddExpertCertificateUseCase = Depends(get_add_expert_certificate_usecase),
) -> None:
    """Добавить удостоверение эксперту."""

    await usecase.execute(
        user_id=user_id,
        payload=payload,
    )


@router.patch("/{user_id}/certificates/{certificate_id}", status_code=204)
async def update_expert_certificate(
    *,
    user_id: int,
    certificate_id: int,
    payload: ExpertCertificateRequest,
    usecase: UpdateExpertCertificateUseCase = Depends(get_update_expert_certificate_usecase),
) -> None:
    """Изменить удостоверение эксперта."""

    await usecase.execute(
        user_id=user_id,
        certificate_id=certificate_id,
        payload=payload,
    )


@router.delete("/{user_id}/certificates/{certificate_id}", status_code=204)
async def delete_expert_certificate(
    *,
    user_id: int,
    certificate_id: int,
    usecase: DeleteExpertCertificateUseCase = Depends(get_delete_expert_certificate_usecase),
) -> None:
    """Удалить удостоверение эксперта."""

    await usecase.execute(
        user_id=user_id,
        certificate_id=certificate_id,
    )
