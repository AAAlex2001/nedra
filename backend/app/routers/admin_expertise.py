from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.admin import require_admin
from app.dependencies.expertise import (
    get_delete_expertise_usecase,
    get_expertise_repository,
    get_update_expertise_usecase,
)
from app.dependencies.users import get_user_repository
from app.models.expertise import Expertise
from app.schemas.expertise import (
    ExpertiseAdminSchema,
    ExpertiseAdminUpdateSchema,
    ExpertiseCompanySchema,
)
from app.services.expertise.exceptions import ExpertiseNotFoundError
from app.services.expertise.repo import ExpertiseRepository
from app.services.expertise.usecases.manage_expertise import (
    DeleteExpertiseUseCase,
    UpdateExpertiseUseCase,
)
from app.services.users.repo import UserRepository


router = APIRouter(
    prefix="/admin/expertises",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


async def to_admin_schema(expertise: Expertise, users: UserRepository) -> ExpertiseAdminSchema:
    """Собрать строку для админки с именами заказчика и эксперта."""

    customer = await users.get_by_id(expertise.customer_id)
    expert = await users.get_by_id(expertise.expert_id) if expertise.expert_id else None

    return ExpertiseAdminSchema(
        id=expertise.id,
        customer_id=expertise.customer_id,
        customer_name=customer.full_name if customer else "—",
        expert_id=expertise.expert_id,
        expert_name=expert.full_name if expert else None,
        object_code=expertise.object_code,
        area_code=expertise.area_code,
        hazard_class=expertise.hazard_class,
        expert_category=expertise.expert_category,
        deadline=expertise.deadline,
        object_name=expertise.object_name,
        contract_kind=expertise.contract_kind,
        company=ExpertiseCompanySchema.model_validate(expertise.company)
        if expertise.company
        else None,
        comment=expertise.comment,
        status=expertise.status,
        price=expertise.price,
        created_at=expertise.created_at,
    )


@router.get("")
async def list_expertises(
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    users: UserRepository = Depends(get_user_repository),
) -> list[ExpertiseAdminSchema]:
    """Все заявки на экспертизу, новые первыми."""

    items = await expertises.list_all()

    return [await to_admin_schema(item, users) for item in items]


@router.patch("/{expertise_id}")
async def update_expertise(
    expertise_id: int,
    payload: ExpertiseAdminUpdateSchema,
    usecase: UpdateExpertiseUseCase = Depends(get_update_expertise_usecase),
    users: UserRepository = Depends(get_user_repository),
) -> ExpertiseAdminSchema:
    """Поменять статус и стоимость заявки."""

    try:
        updated = await usecase.execute(expertise_id, payload.status, payload.price)
    except ExpertiseNotFoundError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error

    return await to_admin_schema(updated, users)


@router.delete("/{expertise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expertise(
    expertise_id: int,
    usecase: DeleteExpertiseUseCase = Depends(get_delete_expertise_usecase),
) -> None:
    """Удалить заявку вместе с файлами."""

    try:
        await usecase.execute(expertise_id)
    except ExpertiseNotFoundError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error
