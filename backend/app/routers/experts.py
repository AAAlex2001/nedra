from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import ValidationError

from app.dependencies.experts import (
    get_add_certificate_usecase,
    get_delete_certificate_usecase,
    get_private_storage,
    get_profile_repository,
    get_submit_application_usecase,
    get_update_certificate_usecase,
)
from app.dependencies.users import require_expert
from app.models.user import User
from app.schemas.expert import (
    AttestationAreaSchema,
    CertificateInSchema,
    CertificateOutSchema,
    DirectionSchema,
    ExpertApplicationCreatedSchema,
    ExpertApplicationInSchema,
    ExpertCatalogSchema,
    ExpertiseObjectSchema,
    ExpertProfileOutSchema,
    HazardClassSchema,
)
from app.services.experts.catalog import (
    AREAS,
    CATEGORIES,
    DIRECTIONS,
    HAZARD_CLASS_CATEGORY,
    OBJECTS,
)
from app.services.experts.exceptions import (
    ApplicationAlreadyPendingError,
    CertificateNotFoundError,
    ContactsRequiredError,
    InvalidCertificateError,
    InvalidDirectionError,
)
from app.services.experts.letters import send_application_received, send_certificate_changed
from app.services.experts.repo import ExpertProfileRepository
from app.services.experts.usecases.manage_certificates import (
    AddCertificateUseCase,
    DeleteCertificateUseCase,
    UpdateCertificateUseCase,
)
from app.services.experts.usecases.submit_application import SubmitExpertApplicationUseCase
from app.services.files.storage import PrivateStorage
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
        hazard_classes=[
            HazardClassSchema(hazard_class=hazard_class, category=category)
            for hazard_class, category in HAZARD_CLASS_CATEGORY.items()
        ],
    )


@router.post("/applications", status_code=status.HTTP_201_CREATED)
async def submit_application(
    background_tasks: BackgroundTasks,
    payload: str = Form(..., description="JSON заявки по схеме ExpertApplicationInSchema"),
    usecase: SubmitExpertApplicationUseCase = Depends(get_submit_application_usecase),
) -> ExpertApplicationCreatedSchema:
    """Подать заявку эксперта.

    Форма приходит как multipart с полем payload, где лежит JSON заявки.
    Аккаунт создаётся при одобрении, поэтому в заявке нужны контакты и пароль.
    """

    try:
        data = ExpertApplicationInSchema.model_validate_json(payload)
    except ValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error.errors(include_url=False),
        ) from error

    try:
        application = await usecase.execute(data)
    except (
        WeakPasswordError,
        InvalidPhoneError,
        InvalidDirectionError,
        InvalidCertificateError,
        ContactsRequiredError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error
    except EmailAlreadyTakenError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Этот email уже занят. Укажите другой адрес для аккаунта эксперта",
        ) from error
    except ApplicationAlreadyPendingError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Заявка с этим email уже на рассмотрении",
        ) from error

    background_tasks.add_task(send_application_received, application)

    return ExpertApplicationCreatedSchema(id=application.id, status=application.status)


async def profile_schema(user: User, profiles: ExpertProfileRepository) -> ExpertProfileOutSchema:
    """Профиль эксперта с актуальным списком удостоверений."""

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


@router.get("/me")
async def get_my_profile(
    user: User = Depends(require_expert),
    profiles: ExpertProfileRepository = Depends(get_profile_repository),
) -> ExpertProfileOutSchema:
    """Профиль текущего эксперта для личного кабинета."""

    return await profile_schema(user, profiles)


@router.post("/me/certificates", status_code=status.HTTP_201_CREATED)
async def add_my_certificate(
    payload: CertificateInSchema,
    background_tasks: BackgroundTasks,
    user: User = Depends(require_expert),
    usecase: AddCertificateUseCase = Depends(get_add_certificate_usecase),
    profiles: ExpertProfileRepository = Depends(get_profile_repository),
) -> ExpertProfileOutSchema:
    """Эксперт добавляет удостоверение, которое забыл указать в заявке."""

    try:
        certificate = await usecase.execute(user.id, payload)
    except InvalidCertificateError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error

    background_tasks.add_task(send_certificate_changed, user, "добавил", certificate)

    return await profile_schema(user, profiles)


@router.patch("/me/certificates/{certificate_id}")
async def update_my_certificate(
    certificate_id: int,
    payload: CertificateInSchema,
    background_tasks: BackgroundTasks,
    user: User = Depends(require_expert),
    usecase: UpdateCertificateUseCase = Depends(get_update_certificate_usecase),
    profiles: ExpertProfileRepository = Depends(get_profile_repository),
) -> ExpertProfileOutSchema:
    """Эксперт правит своё удостоверение."""

    try:
        certificate = await usecase.execute(user.id, certificate_id, payload)
    except CertificateNotFoundError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error
    except InvalidCertificateError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error

    background_tasks.add_task(send_certificate_changed, user, "изменил", certificate)

    return await profile_schema(user, profiles)


@router.delete("/me/certificates/{certificate_id}")
async def delete_my_certificate(
    certificate_id: int,
    background_tasks: BackgroundTasks,
    user: User = Depends(require_expert),
    usecase: DeleteCertificateUseCase = Depends(get_delete_certificate_usecase),
    profiles: ExpertProfileRepository = Depends(get_profile_repository),
) -> ExpertProfileOutSchema:
    """Эксперт удаляет своё удостоверение. Последнее удалить нельзя."""

    try:
        certificate = await usecase.execute(user.id, certificate_id)
    except CertificateNotFoundError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error
    except InvalidCertificateError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error

    background_tasks.add_task(send_certificate_changed, user, "удалил", certificate)

    return await profile_schema(user, profiles)


@router.get("/me/certificates/{certificate_id}/scan")
async def get_my_certificate_scan(
    certificate_id: int,
    user: User = Depends(require_expert),
    profiles: ExpertProfileRepository = Depends(get_profile_repository),
    storage: PrivateStorage = Depends(get_private_storage),
) -> FileResponse:
    """Скан собственного удостоверения. Открывается в браузере."""

    certificate = await profiles.get_certificate(user.id, certificate_id)
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
