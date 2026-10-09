from datetime import datetime, timezone
from typing import NoReturn
from urllib.parse import quote

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Response, UploadFile, status
from pydantic import ValidationError

from app.dependencies.audit import (
    get_answer_counter_usecase,
    get_answer_offer_usecase,
    get_approve_plan_usecase,
    get_create_audit_usecase,
    get_propose_price_usecase,
    get_request_plan_changes_usecase,
    get_send_plan_usecase,
    get_set_team_usecase,
    get_upload_audit_documents_usecase,
)
from app.dependencies.experts import get_profile_repository
from app.dependencies.expertise import get_expertise_presenter, get_visible_expertise
from app.dependencies.users import get_user_repository, require_customer, require_expert
from app.models.expertise import Expertise, ServiceKind
from app.models.user import User
from app.schemas.audit import (
    AuditChecklistItemSchema,
    AuditCounterAnswerSchema,
    AuditInSchema,
    AuditOfferAnswerSchema,
    AuditPlanChangesSchema,
    AuditPriceSchema,
    AuditTeamSchema,
)
from app.schemas.audit_details import AuditPlanInSchema, AuditPlanSchema, AuditTeamMemberSchema
from app.schemas.expertise import ExpertiseOutSchema
from app.services.audit.checklist import AUDIT_DOCUMENTS
from app.services.audit.invite import build_invite
from app.services.audit.letters import (
    send_consultation_letter,
    send_counter_answered_letter,
    send_offer_answered_letter,
    send_offer_letter,
    send_plan_approved_letters,
    send_plan_changes_letter,
    send_plan_letter,
)
from app.services.audit.report import build_documents_report, report_filename
from app.services.audit.team import describe_member, load_team
from app.services.audit.usecases.create_audit import CreateAuditUseCase
from app.services.audit.usecases.negotiate import (
    AnswerCounterUseCase,
    AnswerOfferUseCase,
    ProposePriceUseCase,
)
from app.services.audit.usecases.plan import (
    ApprovePlanUseCase,
    RequestPlanChangesUseCase,
    SendPlanUseCase,
    team_ids,
)
from app.services.audit.usecases.team import SetAuditTeamUseCase
from app.services.audit.usecases.upload_documents import UploadAuditDocumentsUseCase
from app.services.billing.exceptions import InvalidCompanyError
from app.services.contracts.document import DOCX_TYPE
from app.services.experts.repo import ExpertProfileRepository
from app.services.expertise.exceptions import (
    ExpertiseAccessError,
    ExpertiseStateError,
    InvalidExpertiseError,
)
from app.services.expertise.letters import send_new_expertise_letters
from app.services.expertise.presenter import ExpertisePresenter
from app.services.files.storage import UploadError
from app.services.users.repo import UserRepository

router = APIRouter(prefix="/audit", tags=["audit"])

FLOW_ERRORS = (ExpertiseStateError, ExpertiseAccessError, InvalidExpertiseError, UploadError)


def raise_for_flow_error(error: Exception) -> NoReturn:
    """Перевести ошибку шага аудита в HTTP-код."""

    if isinstance(error, ExpertiseStateError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error

    if isinstance(error, ExpertiseAccessError):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)
    ) from error


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
    opo_certificate: UploadFile | None = File(
        default=None, description="Свидетельство о регистрации ОПО, когда аудит по всем ОПО"
    ),
    power_of_attorney: UploadFile | None = File(
        default=None, description="Доверенность, если заявитель не руководитель"
    ),
    sto_file: UploadFile | None = File(default=None, description="Файл СТО организации"),
    customer: User = Depends(require_customer),
    usecase: CreateAuditUseCase = Depends(get_create_audit_usecase),
    presenter: ExpertisePresenter = Depends(get_expertise_presenter),
) -> ExpertiseOutSchema:
    """Подать заявку на аудит СУПБ. Руководители групп получат уведомление и письмо,
    а при запросе консультации заявку сначала получает менеджер."""

    try:
        data = AuditInSchema.model_validate_json(payload)
    except ValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error.errors(include_url=False),
        ) from error

    try:
        created = await usecase.execute(
            customer,
            data,
            files,
            items,
            company_card,
            opo_certificate,
            power_of_attorney,
            sto_file,
        )
    except (InvalidExpertiseError, InvalidCompanyError, UploadError) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

    if data.details.params.kind == "consultation":
        background_tasks.add_task(send_consultation_letter, created.expertise)
    else:
        background_tasks.add_task(
            send_new_expertise_letters, created.expertise, created.notified_experts
        )

    return await presenter.build(created.expertise)


@router.get("/auditors")
async def list_auditors(
    expert: User = Depends(require_expert),
    profiles: ExpertProfileRepository = Depends(get_profile_repository),
    users: UserRepository = Depends(get_user_repository),
) -> list[AuditTeamMemberSchema]:
    """Аудиторы, которых руководитель группы может включить в группу."""

    if not await profiles.is_audit_lead(expert.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Список аудиторов доступен руководителю аудиторской группы",
        )

    auditors = await profiles.list_auditors()
    members: list[AuditTeamMemberSchema] = []

    for auditor in auditors:
        if auditor.id == expert.id:
            continue

        member = await describe_member(auditor.id, False, users, profiles)
        if member is not None:
            members.append(
                AuditTeamMemberSchema(
                    user_id=member.user_id,
                    full_name=member.full_name,
                    areas=member.areas,
                    lead=False,
                )
            )

    return members


@router.post("/{expertise_id}/offer")
async def propose_price(
    payload: AuditPriceSchema,
    background_tasks: BackgroundTasks,
    audit: Expertise = Depends(get_visible_expertise),
    lead: User = Depends(require_expert),
    usecase: ProposePriceUseCase = Depends(get_propose_price_usecase),
    users: UserRepository = Depends(get_user_repository),
    presenter: ExpertisePresenter = Depends(get_expertise_presenter),
) -> ExpertiseOutSchema:
    """Руководитель группы предлагает заказчику свою цену."""

    try:
        updated = await usecase.execute(lead, audit, payload.price)
    except FLOW_ERRORS as error:
        raise_for_flow_error(error)

    customer = await users.get_by_id(updated.customer_id)
    if customer is not None:
        background_tasks.add_task(send_offer_letter, updated, customer)

    return await presenter.build(updated)


@router.post("/{expertise_id}/offer/answer")
async def answer_offer(
    payload: AuditOfferAnswerSchema,
    background_tasks: BackgroundTasks,
    audit: Expertise = Depends(get_visible_expertise),
    customer: User = Depends(require_customer),
    usecase: AnswerOfferUseCase = Depends(get_answer_offer_usecase),
    users: UserRepository = Depends(get_user_repository),
    presenter: ExpertisePresenter = Depends(get_expertise_presenter),
) -> ExpertiseOutSchema:
    """Заказчик принимает цену аудитора, понижает её или отказывается."""

    lead_id = audit.expert_id

    try:
        updated = await usecase.execute(customer, audit, payload.answer, payload.price)
    except FLOW_ERRORS as error:
        raise_for_flow_error(error)

    lead = await users.get_by_id(lead_id) if lead_id is not None else None
    if lead is not None:
        background_tasks.add_task(send_offer_answered_letter, updated, lead, payload.answer)

    return await presenter.build(updated)


@router.post("/{expertise_id}/counter/answer")
async def answer_counter(
    payload: AuditCounterAnswerSchema,
    background_tasks: BackgroundTasks,
    audit: Expertise = Depends(get_visible_expertise),
    lead: User = Depends(require_expert),
    usecase: AnswerCounterUseCase = Depends(get_answer_counter_usecase),
    users: UserRepository = Depends(get_user_repository),
    presenter: ExpertisePresenter = Depends(get_expertise_presenter),
) -> ExpertiseOutSchema:
    """Руководитель группы принимает цену заказчика или отказывается от заявки."""

    try:
        updated = await usecase.execute(lead, audit, payload.accept)
    except FLOW_ERRORS as error:
        raise_for_flow_error(error)

    customer = await users.get_by_id(updated.customer_id)
    if customer is not None:
        background_tasks.add_task(send_counter_answered_letter, updated, customer, payload.accept)

    return await presenter.build(updated)


@router.put("/{expertise_id}/team")
async def set_team(
    payload: AuditTeamSchema,
    audit: Expertise = Depends(get_visible_expertise),
    lead: User = Depends(require_expert),
    usecase: SetAuditTeamUseCase = Depends(get_set_team_usecase),
    presenter: ExpertisePresenter = Depends(get_expertise_presenter),
) -> ExpertiseOutSchema:
    """Руководитель группы задаёт состав аудиторской группы."""

    try:
        updated = await usecase.execute(lead, audit, payload.user_ids)
    except FLOW_ERRORS as error:
        raise_for_flow_error(error)

    return await presenter.build(updated)


@router.post("/{expertise_id}/plan")
async def send_plan(
    payload: AuditPlanInSchema,
    background_tasks: BackgroundTasks,
    audit: Expertise = Depends(get_visible_expertise),
    lead: User = Depends(require_expert),
    usecase: SendPlanUseCase = Depends(get_send_plan_usecase),
    users: UserRepository = Depends(get_user_repository),
    profiles: ExpertProfileRepository = Depends(get_profile_repository),
    presenter: ExpertisePresenter = Depends(get_expertise_presenter),
) -> ExpertiseOutSchema:
    """Руководитель группы отправляет заказчику План аудита на согласование."""

    team = await load_team(audit, users, profiles)

    try:
        updated = await usecase.execute(lead, audit, payload, team)
    except FLOW_ERRORS as error:
        raise_for_flow_error(error)

    customer = await users.get_by_id(updated.customer_id)
    if customer is not None:
        background_tasks.add_task(send_plan_letter, updated, customer)

    return await presenter.build(updated)


@router.post("/{expertise_id}/plan/approve")
async def approve_plan(
    background_tasks: BackgroundTasks,
    audit: Expertise = Depends(get_visible_expertise),
    customer: User = Depends(require_customer),
    usecase: ApprovePlanUseCase = Depends(get_approve_plan_usecase),
    users: UserRepository = Depends(get_user_repository),
    presenter: ExpertisePresenter = Depends(get_expertise_presenter),
) -> ExpertiseOutSchema:
    """Заказчик согласует План: открывается проверка документов, группе и заказчику —
    письма с приглашением на вступительное совещание."""

    try:
        updated = await usecase.execute(customer, audit)
    except FLOW_ERRORS as error:
        raise_for_flow_error(error)

    team: list[User] = []
    for user_id in team_ids(updated):
        member = await users.get_by_id(user_id)
        if member is not None:
            team.append(member)

    plan = AuditPlanSchema.model_validate(updated.audit_plan)
    invite = build_invite(updated, plan, datetime.now(timezone.utc))
    background_tasks.add_task(send_plan_approved_letters, updated, customer, team, invite)

    return await presenter.build(updated)


@router.post("/{expertise_id}/plan/changes")
async def request_plan_changes(
    payload: AuditPlanChangesSchema,
    background_tasks: BackgroundTasks,
    audit: Expertise = Depends(get_visible_expertise),
    customer: User = Depends(require_customer),
    usecase: RequestPlanChangesUseCase = Depends(get_request_plan_changes_usecase),
    users: UserRepository = Depends(get_user_repository),
    presenter: ExpertisePresenter = Depends(get_expertise_presenter),
) -> ExpertiseOutSchema:
    """Заказчик просит скорректировать План аудита."""

    try:
        updated = await usecase.execute(customer, audit, payload.comment)
    except FLOW_ERRORS as error:
        raise_for_flow_error(error)

    lead = await users.get_by_id(updated.expert_id) if updated.expert_id else None
    if lead is not None:
        background_tasks.add_task(send_plan_changes_letter, updated, lead)

    return await presenter.build(updated)


@router.post("/{expertise_id}/documents")
async def upload_documents(
    files: list[UploadFile] = File(default=[], description="Документы по перечню"),
    items: list[int] = Form(default=[], description="Номер пункта перечня для каждого файла по порядку"),
    audit: Expertise = Depends(get_visible_expertise),
    customer: User = Depends(require_customer),
    usecase: UploadAuditDocumentsUseCase = Depends(get_upload_audit_documents_usecase),
    presenter: ExpertisePresenter = Depends(get_expertise_presenter),
) -> ExpertiseOutSchema:
    """Заказчик загружает документы по перечню после согласования Плана."""

    try:
        updated = await usecase.execute(customer, audit, files, items)
    except FLOW_ERRORS as error:
        raise_for_flow_error(error)

    return await presenter.build(updated)


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
