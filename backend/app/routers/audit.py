from datetime import datetime, timezone
from urllib.parse import quote

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Response, UploadFile, status
from pydantic import ValidationError

from app.dependencies.audit import get_create_audit_usecase
from app.dependencies.expertise import get_visible_expertise
from app.dependencies.payments import get_payment_repository
from app.dependencies.users import get_user_repository, require_customer
from app.models.expertise import Expertise, ServiceKind
from app.models.user import User
from app.routers.expertise import to_schema
from app.schemas.audit import AuditChecklistItemSchema, AuditInSchema
from app.schemas.expertise import ExpertiseOutSchema
from app.services.audit.checklist import AUDIT_DOCUMENTS
from app.services.audit.report import build_documents_report, report_filename
from app.services.audit.usecases.create_audit import CreateAuditUseCase
from app.services.billing.exceptions import InvalidCompanyError
from app.services.contracts.document import DOCX_TYPE
from app.services.expertise.exceptions import InvalidExpertiseError
from app.services.expertise.letters import send_new_expertise_letters
from app.services.files.storage import UploadError
from app.services.payments.repo import PaymentRepository
from app.services.users.repo import UserRepository

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/checklist")
async def get_checklist() -> list[AuditChecklistItemSchema]:
    """Перечень документов для аудита СУПБ с номерами пунктов."""

    return [
        AuditChecklistItemSchema(number=number, title=title)
        for number, title in enumerate(AUDIT_DOCUMENTS, start=1)
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_audit(
    background_tasks: BackgroundTasks,
    payload: str = Form(..., description="JSON заявки по схеме AuditInSchema"),
    files: list[UploadFile] = File(default=[], description="Документы по перечню"),
    items: list[int] = Form(default=[], description="Номер пункта перечня для каждого файла по порядку"),
    company_card: UploadFile | None = File(
        default=None, description="Карточка организации заказчика с реквизитами"
    ),
    customer: User = Depends(require_customer),
    usecase: CreateAuditUseCase = Depends(get_create_audit_usecase),
    users: UserRepository = Depends(get_user_repository),
    payments: PaymentRepository = Depends(get_payment_repository),
) -> ExpertiseOutSchema:
    """Подать заявку на аудит СУПБ. Аудиторы получат уведомление и письмо."""

    try:
        data = AuditInSchema.model_validate_json(payload)
    except ValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error.errors(include_url=False),
        ) from error

    try:
        created = await usecase.execute(customer, data, files, items, company_card)
    except (InvalidExpertiseError, InvalidCompanyError, UploadError) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

    background_tasks.add_task(send_new_expertise_letters, created.expertise, created.notified_experts)

    return await to_schema(created.expertise, users, payments)


@router.get("/{expertise_id}/documents-report")
async def download_documents_report(
    expertise: Expertise = Depends(get_visible_expertise),
) -> Response:
    """Отчёт о представленных документах в Word: что из перечня загружено, а что нет."""

    if expertise.service != ServiceKind.AUDIT:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Это не заявка на аудит")

    content = build_documents_report(expertise, datetime.now(timezone.utc))
    filename = quote(report_filename(expertise))

    return Response(
        content=content,
        media_type=DOCX_TYPE,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )
