"""Подача и просмотр заявок."""

from fastapi import APIRouter, Depends

from src.audit.schemas.audit import AuditResponse
from src.audit.schemas.audit_application import AuditApplicationResponse
from src.audit.schemas.audit_participants import AuditCustomerResponse
from src.audit.site.audit_upload_files import AuditUploadFiles
from src.audit.site.request_dependencies import (
    get_accept_audit_usecase,
    get_audit_application_usecase,
    get_audit_customer_usecase,
    get_audit_upload_files,
    get_audit_usecase,
    get_create_audit_usecase,
    get_list_audits_usecase,
    parse_audit_form,
)
from src.audit.site.schemas.create_audit import CreateAuditRequest
from src.audit.site.schemas.list_audits import AuditListItemResponse
from src.audit.site.usecases.accept_audit import AcceptAuditUseCase
from src.audit.site.usecases.create_audit import CreateAuditUseCase
from src.audit.site.usecases.get_audit import GetAuditUseCase
from src.audit.site.usecases.get_audit_application import GetAuditApplicationUseCase
from src.audit.site.usecases.get_audit_customer import GetAuditCustomerUseCase
from src.audit.site.usecases.list_audits import ListAuditsUseCase
from src.auth.site.dependencies import get_current_user, require_customer, require_expert
from src.users.models.user import User

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
)


@router.get("/my")
async def list_my_audits(
    *,
    user: User = Depends(require_customer),
    usecase: ListAuditsUseCase = Depends(get_list_audits_usecase),
) -> list[AuditListItemResponse]:
    """Получить свои работы."""

    return await usecase.execute(
        user=user,
        scope="my",
    )


@router.get("/incoming")
async def list_incoming_audits(
    *,
    user: User = Depends(require_expert),
    usecase: ListAuditsUseCase = Depends(get_list_audits_usecase),
) -> list[AuditListItemResponse]:
    """Получить входящие работы."""

    return await usecase.execute(
        user=user,
        scope="incoming",
    )


@router.get("/assigned")
async def list_assigned_audits(
    *,
    user: User = Depends(require_expert),
    usecase: ListAuditsUseCase = Depends(get_list_audits_usecase),
) -> list[AuditListItemResponse]:
    """Получить назначенные работы."""

    return await usecase.execute(
        user=user,
        scope="assigned",
    )


@router.post("", status_code=201)
async def create_audit(
    *,
    payload: CreateAuditRequest = Depends(parse_audit_form),
    files: AuditUploadFiles = Depends(get_audit_upload_files),
    user: User = Depends(require_customer),
    usecase: CreateAuditUseCase = Depends(get_create_audit_usecase),
) -> AuditResponse:
    """Подать заявку на аудит."""

    return await usecase.execute(
        user=user,
        payload=payload,
        files=files,
    )


@router.get("/{audit_id}")
async def get_audit(
    *,
    audit_id: int,
    user: User = Depends(get_current_user),
    usecase: GetAuditUseCase = Depends(get_audit_usecase),
) -> AuditResponse:
    """Открыть карточку услуги."""

    return await usecase.execute(
        audit_id=audit_id,
        user=user,
    )


@router.post("/{audit_id}/accept")
async def accept_audit(
    *,
    audit_id: int,
    user: User = Depends(require_expert),
    usecase: AcceptAuditUseCase = Depends(get_accept_audit_usecase),
) -> AuditResponse:
    """Принять заявку в работу."""

    return await usecase.execute(
        audit_id=audit_id,
        user=user,
    )


@router.get("/{audit_id}/customer")
async def get_audit_customer(
    *,
    audit_id: int,
    user: User = Depends(get_current_user),
    usecase: GetAuditCustomerUseCase = Depends(get_audit_customer_usecase),
) -> AuditCustomerResponse:
    """Заказчик аудита."""

    return await usecase.execute(
        audit_id=audit_id,
        user=user,
    )


@router.get("/{audit_id}/application")
async def get_audit_application(
    *,
    audit_id: int,
    user: User = Depends(get_current_user),
    usecase: GetAuditApplicationUseCase = Depends(get_audit_application_usecase),
) -> AuditApplicationResponse | None:
    """Анкета заказчика."""

    return await usecase.execute(
        audit_id=audit_id,
        user=user,
    )
