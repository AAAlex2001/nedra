from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import ValidationError

from app.dependencies.experts import get_private_storage, get_profile_repository
from app.dependencies.expertise import (
    get_create_expertise_usecase,
    get_expertise_repository,
    get_visible_expertise,
)
from app.dependencies.users import require_customer, require_expert
from app.models.expertise import Expertise
from app.models.user import User
from app.schemas.expertise import ExpertiseInSchema, ExpertiseOutSchema
from app.services.experts.repo import ExpertProfileRepository
from app.services.expertise.exceptions import InvalidExpertiseError
from app.services.expertise.letters import send_new_expertise_letters
from app.services.expertise.repo import ExpertiseRepository
from app.services.expertise.usecases.create_expertise import CreateExpertiseUseCase
from app.services.files.storage import PrivateStorage, UploadError
from app.services.users.repo import UserRepository
from app.dependencies.users import get_user_repository


router = APIRouter(prefix="/expertise", tags=["expertise"])


async def to_schema(expertise: Expertise, users: UserRepository) -> ExpertiseOutSchema:
    """Собрать схему с именем заказчика: эксперту нужно видеть, от кого заявка."""

    customer = await users.get_by_id(expertise.customer_id)
    customer_name = customer.full_name if customer else "—"

    return ExpertiseOutSchema(
        id=expertise.id,
        customer_id=expertise.customer_id,
        customer_name=customer_name,
        expert_id=expertise.expert_id,
        object_code=expertise.object_code,
        area_code=expertise.area_code,
        hazard_class=expertise.hazard_class,
        expert_category=expertise.expert_category,
        comment=expertise.comment,
        status=expertise.status,
        created_at=expertise.created_at,
        documents=expertise.documents,
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_expertise(
    background_tasks: BackgroundTasks,
    payload: str = Form(..., description="JSON заявки по схеме ExpertiseInSchema"),
    files: list[UploadFile] = File(default=[], description="Документация: PDF, Word, фото"),
    customer: User = Depends(require_customer),
    usecase: CreateExpertiseUseCase = Depends(get_create_expertise_usecase),
    users: UserRepository = Depends(get_user_repository),
) -> ExpertiseOutSchema:
    """Подать документацию на экспертизу. Подходящие эксперты получат уведомление и письмо."""

    try:
        data = ExpertiseInSchema.model_validate_json(payload)
    except ValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error.errors(include_url=False),
        ) from error

    try:
        created = await usecase.execute(customer, data, files)
    except (InvalidExpertiseError, UploadError) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

    background_tasks.add_task(send_new_expertise_letters, created.expertise, created.notified_experts)

    return await to_schema(created.expertise, users)


@router.get("/my")
async def list_my_expertises(
    customer: User = Depends(require_customer),
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    users: UserRepository = Depends(get_user_repository),
) -> list[ExpertiseOutSchema]:
    """Заявки текущего заказчика."""

    items = await expertises.list_for_customer(customer.id)

    return [await to_schema(item, users) for item in items]


@router.get("/incoming")
async def list_incoming_expertises(
    object_code: str | None = Query(None, description="Фильтр по объекту экспертизы"),
    area_code: str | None = Query(None, description="Фильтр по области аттестации"),
    expert: User = Depends(require_expert),
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    profiles: ExpertProfileRepository = Depends(get_profile_repository),
    users: UserRepository = Depends(get_user_repository),
) -> list[ExpertiseOutSchema]:
    """Новые заявки, подходящие под удостоверения эксперта."""

    certificates = await profiles.list_certificates(expert.id)
    items = await expertises.list_incoming(certificates, object_code, area_code)

    return [await to_schema(item, users) for item in items]


@router.get("/{expertise_id}")
async def get_expertise(
    expertise: Expertise = Depends(get_visible_expertise),
    users: UserRepository = Depends(get_user_repository),
) -> ExpertiseOutSchema:
    """Одна экспертиза для заказчика или эксперта."""

    return await to_schema(expertise, users)


@router.get("/{expertise_id}/documents/{document_id}")
async def download_document(
    document_id: int,
    expertise: Expertise = Depends(get_visible_expertise),
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    storage: PrivateStorage = Depends(get_private_storage),
) -> FileResponse:
    """Файл экспертизы. Доступен только участникам."""

    document = await expertises.get_document(expertise.id, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Документ не найден",
        )

    try:
        path = storage.resolve(document.file_path)
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл отсутствует на диске",
        ) from error

    return FileResponse(path, filename=document.original_name)
