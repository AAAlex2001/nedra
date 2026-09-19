from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import ValidationError

from app.dependencies.experts import (
    get_private_storage,
    get_profile_repository,
    get_submit_application_usecase,
)
from app.dependencies.users import require_expert
from app.models.user import User
from app.schemas.expert import (
    AttestationAreaSchema,
    CertificateOutSchema,
    DirectionSchema,
    ExpertApplicationCreatedSchema,
    ExpertApplicationInSchema,
    ExpertCatalogSchema,
    ExpertiseObjectSchema,
    ExpertProfileOutSchema,
    PublicCertificateSchema,
    PublicExpertSchema,
)
from app.services.experts.catalog import AREAS, CATEGORIES, DIRECTIONS, OBJECTS
from app.services.experts.exceptions import (
    ApplicationAlreadyPendingError,
    InvalidCertificateError,
    InvalidDirectionError,
)
from app.services.experts.letters import send_application_received
from app.services.experts.repo import ExpertProfileRepository
from app.services.experts.usecases.submit_application import SubmitExpertApplicationUseCase
from app.services.files.storage import PrivateStorage, UploadError
from app.services.users.exceptions import EmailAlreadyTakenError, InvalidPhoneError, WeakPasswordError


router = APIRouter(prefix="/experts", tags=["experts"])


@router.get("/catalog")
async def get_catalog() -> ExpertCatalogSchema:
    """Справочник для формы заявки: направления, области аттестации, объекты, категории."""

    return ExpertCatalogSchema(
        directions=[DirectionSchema(code=item.code, title=item.title) for item in DIRECTIONS],
        areas=[
            AttestationAreaSchema(code=area.code, title=area.title, objects=list(area.objects))
            for area in AREAS
        ],
        objects=[
            ExpertiseObjectSchema(
                code=item.code,
                label=item.label,
                title=item.title,
                description=item.description,
            )
            for item in OBJECTS
        ],
        categories=list(CATEGORIES),
    )


@router.get("/directory")
async def get_directory(
    profiles: ExpertProfileRepository = Depends(get_profile_repository),
) -> list[PublicExpertSchema]:
    """Публичный каталог экспертов с действующими удостоверениями для страницы «Блиц-эксперт»."""

    experts = await profiles.list_public()

    return [
        PublicExpertSchema(
            id=expert.user.id,
            full_name=expert.user.full_name,
            directions=expert.profile.directions,
            approved_at=expert.profile.approved_at,
            certificates=[
                PublicCertificateSchema.model_validate(item) for item in expert.certificates
            ],
        )
        for expert in experts
    ]


@router.get("/directory/{expert_id}/certificates/{certificate_id}/scan")
async def get_certificate_scan(
    expert_id: int,
    certificate_id: int,
    profiles: ExpertProfileRepository = Depends(get_profile_repository),
    storage: PrivateStorage = Depends(get_private_storage),
) -> FileResponse:
    """Скан удостоверения одобренного эксперта. Открывается в браузере, а не скачивается."""

    certificate = await profiles.get_certificate(expert_id, certificate_id)
    if certificate is None or certificate.scan_path is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Скан не найден",
        )

    try:
        path = storage.resolve(certificate.scan_path)
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл скана отсутствует",
        ) from error

    return FileResponse(path, content_disposition_type="inline")


@router.post("/applications", status_code=status.HTTP_201_CREATED)
async def submit_application(
    background_tasks: BackgroundTasks,
    payload: str = Form(..., description="JSON заявки по схеме ExpertApplicationInSchema"),
    scans: list[UploadFile] = File(default=[], description="Сканы удостоверений"),
    usecase: SubmitExpertApplicationUseCase = Depends(get_submit_application_usecase),
) -> ExpertApplicationCreatedSchema:
    """Подать заявку на регистрацию эксперта.

    Форма приходит как multipart: поле payload с JSON и файлы scans.
    Удостоверение ссылается на свой скан через scan_index.
    """

    try:
        data = ExpertApplicationInSchema.model_validate_json(payload)
    except ValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error.errors(include_url=False),
        ) from error

    try:
        application = await usecase.execute(data, scans)
    except (
        WeakPasswordError,
        InvalidPhoneError,
        InvalidDirectionError,
        InvalidCertificateError,
        UploadError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error
    except EmailAlreadyTakenError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже зарегистрирован",
        ) from error
    except ApplicationAlreadyPendingError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Заявка с этим email уже на рассмотрении",
        ) from error

    background_tasks.add_task(send_application_received, application)

    return ExpertApplicationCreatedSchema(id=application.id, status=application.status)


@router.get("/me")
async def get_my_profile(
    user: User = Depends(require_expert),
    profiles: ExpertProfileRepository = Depends(get_profile_repository),
) -> ExpertProfileOutSchema:
    """Профиль текущего эксперта для личного кабинета."""

    profile = await profiles.get_by_user(user.id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль эксперта не найден",
        )

    certificates = await profiles.list_certificates(user.id)

    return ExpertProfileOutSchema(
        directions=profile.directions,
        approved_at=profile.approved_at,
        certificates=[CertificateOutSchema.model_validate(item) for item in certificates],
    )
