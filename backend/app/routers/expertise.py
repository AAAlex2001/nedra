import logging
from typing import NoReturn

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from pydantic import ValidationError

from app.dependencies.experts import get_private_storage, get_profile_repository
from app.dependencies.expertise import (
    get_accept_expertise_usecase,
    get_accept_work_usecase,
    get_apply_expertise_payment_usecase,
    get_confirm_expertise_usecase,
    get_create_expertise_payment_usecase,
    get_create_expertise_usecase,
    get_expertise_repository,
    get_mark_conclusion_ready_usecase,
    get_resubmit_documentation_usecase,
    get_send_conclusion_usecase,
    get_send_remarks_usecase,
    get_visible_expertise,
)
from app.dependencies.payments import get_payment_repository, get_sync_payment_usecase
from app.dependencies.users import get_user_repository, require_customer, require_expert
from app.models.expertise import Expertise
from app.models.payment import PaymentStatus
from app.models.user import User
from app.schemas.expertise import ExpertiseInSchema, ExpertiseOutSchema, ExpertisePaymentSchema
from app.schemas.payment import PaymentOutSchema
from app.services.experts.repo import ExpertProfileRepository
from app.services.expertise.exceptions import (
    ExpertiseAccessError,
    ExpertiseStateError,
    InvalidExpertiseError,
    PriceMissingError,
)
from app.services.expertise.letters import (
    send_advance_paid_letter,
    send_conclusion_ready_letter,
    send_conclusion_sent_letter,
    send_contract_letter,
    send_expert_ready_letter,
    send_final_paid_letter,
    send_new_expertise_letters,
    send_remarks_letter,
    send_revision_letter,
    send_work_accepted_letter,
)
from app.services.expertise.repo import ExpertiseRepository
from app.services.expertise.usecases.accept_expertise import AcceptExpertiseUseCase
from app.services.expertise.usecases.accept_work import AcceptWorkUseCase
from app.services.expertise.usecases.apply_expertise_payment import ApplyExpertisePaymentUseCase
from app.services.expertise.usecases.confirm_expertise import ConfirmExpertiseUseCase
from app.services.expertise.usecases.create_expertise import CreateExpertiseUseCase
from app.services.expertise.usecases.create_expertise_payment import CreateExpertisePaymentUseCase
from app.services.expertise.usecases.mark_conclusion_ready import MarkConclusionReadyUseCase
from app.services.expertise.usecases.resubmit_documentation import ResubmitDocumentationUseCase
from app.services.expertise.usecases.send_conclusion import SendConclusionUseCase
from app.services.expertise.usecases.send_remarks import SendRemarksUseCase
from app.services.files.storage import PrivateStorage, UploadError
from app.services.payments.exceptions import PaymentGatewayError
from app.services.payments.repo import PaymentRepository
from app.services.payments.usecases.sync_payment_status import SyncPaymentStatusUseCase
from app.services.users.repo import UserRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/expertise", tags=["expertise"])


async def to_schema(
    expertise: Expertise, users: UserRepository, payments: PaymentRepository
) -> ExpertiseOutSchema:
    """Собрать схему с именами сторон и платежами по этапам."""

    customer = await users.get_by_id(expertise.customer_id)
    expert = await users.get_by_id(expertise.expert_id) if expertise.expert_id else None

    advance = None
    if expertise.advance_payment_id is not None:
        advance = await payments.get_by_id(expertise.advance_payment_id)

    final = None
    if expertise.final_payment_id is not None:
        final = await payments.get_by_id(expertise.final_payment_id)

    return ExpertiseOutSchema(
        id=expertise.id,
        customer_id=expertise.customer_id,
        customer_name=customer.full_name if customer else "—",
        expert_id=expertise.expert_id,
        expert_name=expert.full_name if expert else None,
        object_code=expertise.object_code,
        area_code=expertise.area_code,
        hazard_class=expertise.hazard_class,
        expert_category=expertise.expert_category,
        comment=expertise.comment,
        status=expertise.status,
        result=expertise.result,
        price=expertise.price,
        advance_payment=ExpertisePaymentSchema.model_validate(advance) if advance else None,
        final_payment=ExpertisePaymentSchema.model_validate(final) if final else None,
        created_at=expertise.created_at,
        expert_ready_at=expertise.expert_ready_at,
        contract_at=expertise.contract_at,
        advance_paid_at=expertise.advance_paid_at,
        conclusion_ready_at=expertise.conclusion_ready_at,
        final_paid_at=expertise.final_paid_at,
        sent_at=expertise.sent_at,
        accepted_at=expertise.accepted_at,
        documents=expertise.documents,
        remarks=expertise.remarks,
    )


def raise_for_flow_error(error: Exception) -> NoReturn:
    """Перевести ошибку шага экспертизы в HTTP-код."""

    if isinstance(error, ExpertiseStateError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error

    if isinstance(error, ExpertiseAccessError):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)
    ) from error


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_expertise(
    background_tasks: BackgroundTasks,
    payload: str = Form(..., description="JSON заявки по схеме ExpertiseInSchema"),
    files: list[UploadFile] = File(default=[], description="Документация: PDF, Word, фото"),
    customer: User = Depends(require_customer),
    usecase: CreateExpertiseUseCase = Depends(get_create_expertise_usecase),
    users: UserRepository = Depends(get_user_repository),
    payments: PaymentRepository = Depends(get_payment_repository),
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

    return await to_schema(created.expertise, users, payments)


@router.get("/my")
async def list_my_expertises(
    customer: User = Depends(require_customer),
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    users: UserRepository = Depends(get_user_repository),
    payments: PaymentRepository = Depends(get_payment_repository),
) -> list[ExpertiseOutSchema]:
    """Заявки текущего заказчика."""

    items = await expertises.list_for_customer(customer.id)

    return [await to_schema(item, users, payments) for item in items]


@router.get("/incoming")
async def list_incoming_expertises(
    object_code: str | None = Query(None, description="Фильтр по объекту экспертизы"),
    area_code: str | None = Query(None, description="Фильтр по области аттестации"),
    expert: User = Depends(require_expert),
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    profiles: ExpertProfileRepository = Depends(get_profile_repository),
    users: UserRepository = Depends(get_user_repository),
    payments: PaymentRepository = Depends(get_payment_repository),
) -> list[ExpertiseOutSchema]:
    """Новые заявки, подходящие под удостоверения эксперта."""

    certificates = await profiles.list_certificates(expert.id)
    items = await expertises.list_incoming(certificates, object_code, area_code)

    return [await to_schema(item, users, payments) for item in items]


@router.get("/assigned")
async def list_assigned_expertises(
    expert: User = Depends(require_expert),
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
    users: UserRepository = Depends(get_user_repository),
    payments: PaymentRepository = Depends(get_payment_repository),
) -> list[ExpertiseOutSchema]:
    """Заявки, которые эксперт взял в работу, на любом шаге."""

    items = await expertises.list_for_expert(expert.id)

    return [await to_schema(item, users, payments) for item in items]


@router.get("/{expertise_id}")
async def get_expertise(
    expertise: Expertise = Depends(get_visible_expertise),
    users: UserRepository = Depends(get_user_repository),
    payments: PaymentRepository = Depends(get_payment_repository),
) -> ExpertiseOutSchema:
    """Одна экспертиза для заказчика или эксперта."""

    return await to_schema(expertise, users, payments)


@router.post("/{expertise_id}/accept")
async def accept_expertise(
    background_tasks: BackgroundTasks,
    expertise: Expertise = Depends(get_visible_expertise),
    expert: User = Depends(require_expert),
    usecase: AcceptExpertiseUseCase = Depends(get_accept_expertise_usecase),
    users: UserRepository = Depends(get_user_repository),
    payments: PaymentRepository = Depends(get_payment_repository),
) -> ExpertiseOutSchema:
    """Шаг 3: эксперт готов провести экспертизу. Заказчику уходит уведомление и письмо."""

    try:
        updated = await usecase.execute(expert, expertise)
    except (ExpertiseStateError, ExpertiseAccessError, PriceMissingError) as error:
        raise_for_flow_error(error)

    customer = await users.get_by_id(updated.customer_id)
    if customer is not None:
        background_tasks.add_task(send_expert_ready_letter, updated, customer, expert)

    return await to_schema(updated, users, payments)


@router.post("/{expertise_id}/confirm")
async def confirm_expertise(
    background_tasks: BackgroundTasks,
    expertise: Expertise = Depends(get_visible_expertise),
    customer: User = Depends(require_customer),
    usecase: ConfirmExpertiseUseCase = Depends(get_confirm_expertise_usecase),
    users: UserRepository = Depends(get_user_repository),
    payments: PaymentRepository = Depends(get_payment_repository),
) -> ExpertiseOutSchema:
    """Шаг 5–6: заказчик готов оплатить, договор заключён."""

    try:
        updated = await usecase.execute(customer, expertise)
    except (ExpertiseStateError, ExpertiseAccessError) as error:
        raise_for_flow_error(error)

    expert = await users.get_by_id(updated.expert_id) if updated.expert_id else None
    if expert is not None:
        background_tasks.add_task(send_contract_letter, updated, expert)

    return await to_schema(updated, users, payments)


@router.post("/{expertise_id}/payment", status_code=status.HTTP_201_CREATED)
async def create_expertise_payment(
    expertise: Expertise = Depends(get_visible_expertise),
    customer: User = Depends(require_customer),
    usecase: CreateExpertisePaymentUseCase = Depends(get_create_expertise_payment_usecase),
) -> PaymentOutSchema:
    """Шаги 7 и 9: платёж за текущий этап. Фронт уводит заказчика по confirmation_url."""

    try:
        payment = await usecase.execute(customer, expertise)
    except (ExpertiseStateError, ExpertiseAccessError, PriceMissingError) as error:
        raise_for_flow_error(error)
    except PaymentGatewayError as error:
        logger.exception("Не удалось создать платёж по экспертизе %s", expertise.id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Платёжный сервис временно недоступен",
        ) from error

    return PaymentOutSchema.model_validate(payment)


@router.post("/{expertise_id}/payment/refresh")
async def refresh_expertise_payment(
    background_tasks: BackgroundTasks,
    expertise: Expertise = Depends(get_visible_expertise),
    customer: User = Depends(require_customer),
    payments: PaymentRepository = Depends(get_payment_repository),
    sync: SyncPaymentStatusUseCase = Depends(get_sync_payment_usecase),
    apply: ApplyExpertisePaymentUseCase = Depends(get_apply_expertise_payment_usecase),
    users: UserRepository = Depends(get_user_repository),
) -> ExpertiseOutSchema:
    """Проверить оплату текущего этапа у ЮKassa. Фронт зовёт после возврата со страницы оплаты."""

    if expertise.customer_id != customer.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Экспертиза не найдена")

    pending_ids = [expertise.advance_payment_id, expertise.final_payment_id]
    updated = expertise

    for payment_id in pending_ids:
        if payment_id is None:
            continue

        payment = await payments.get_by_id(payment_id)
        if payment is None or payment.status == PaymentStatus.SUCCEEDED:
            continue

        try:
            synced = await sync.execute(payment.provider_payment_id)
        except PaymentGatewayError as error:
            logger.exception("Не удалось проверить платёж %s", payment_id)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Платёжный сервис временно недоступен",
            ) from error

        applied = await apply.execute(synced)
        if applied is not None:
            updated = applied
            schedule_payment_letter(background_tasks, applied, synced.id, users)

    return await to_schema(updated, users, payments)


async def notify_expert_about_payment(
    expertise: Expertise, payment_id: int, users: UserRepository
) -> None:
    """Письмо эксперту после оплаты аванса или остатка."""

    if expertise.expert_id is None:
        return

    expert = await users.get_by_id(expertise.expert_id)
    if expert is None:
        return

    if payment_id == expertise.advance_payment_id:
        await send_advance_paid_letter(expertise, expert)
    elif payment_id == expertise.final_payment_id:
        await send_final_paid_letter(expertise, expert)


def schedule_payment_letter(
    background_tasks: BackgroundTasks, expertise: Expertise, payment_id: int, users: UserRepository
) -> None:
    """Поставить письмо эксперту об оплате в фон, чтобы не задерживать ответ."""

    background_tasks.add_task(notify_expert_about_payment, expertise, payment_id, users)


@router.post("/{expertise_id}/conclusion-ready")
async def mark_conclusion_ready(
    background_tasks: BackgroundTasks,
    expertise: Expertise = Depends(get_visible_expertise),
    expert: User = Depends(require_expert),
    usecase: MarkConclusionReadyUseCase = Depends(get_mark_conclusion_ready_usecase),
    users: UserRepository = Depends(get_user_repository),
    payments: PaymentRepository = Depends(get_payment_repository),
) -> ExpertiseOutSchema:
    """Шаг 8: эксперт сообщает, что заключение готово."""

    try:
        updated = await usecase.execute(expert, expertise)
    except (ExpertiseStateError, ExpertiseAccessError) as error:
        raise_for_flow_error(error)

    customer = await users.get_by_id(updated.customer_id)
    if customer is not None:
        background_tasks.add_task(send_conclusion_ready_letter, updated, customer)

    return await to_schema(updated, users, payments)


@router.post("/{expertise_id}/remarks")
async def send_remarks(
    background_tasks: BackgroundTasks,
    text: str | None = Form(None, description="Текст замечаний"),
    files: list[UploadFile] = File(default=[], description="Файл с замечаниями: PDF или Word"),
    expertise: Expertise = Depends(get_visible_expertise),
    expert: User = Depends(require_expert),
    usecase: SendRemarksUseCase = Depends(get_send_remarks_usecase),
    users: UserRepository = Depends(get_user_repository),
    payments: PaymentRepository = Depends(get_payment_repository),
) -> ExpertiseOutSchema:
    """Шаг 8а: эксперт выдаёт замечания вместо готового заключения."""

    try:
        updated = await usecase.execute(expert, expertise, text, files)
    except (ExpertiseStateError, ExpertiseAccessError, InvalidExpertiseError, UploadError) as error:
        raise_for_flow_error(error)

    customer = await users.get_by_id(updated.customer_id)
    if customer is not None:
        background_tasks.add_task(send_remarks_letter, updated, customer, text)

    return await to_schema(updated, users, payments)


@router.post("/{expertise_id}/revision")
async def resubmit_documentation(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(default=[], description="Исправленная документация"),
    expertise: Expertise = Depends(get_visible_expertise),
    customer: User = Depends(require_customer),
    usecase: ResubmitDocumentationUseCase = Depends(get_resubmit_documentation_usecase),
    users: UserRepository = Depends(get_user_repository),
    payments: PaymentRepository = Depends(get_payment_repository),
) -> ExpertiseOutSchema:
    """Шаг 8б: заказчик исправил замечания и отправляет документацию повторно."""

    try:
        updated = await usecase.execute(customer, expertise, files)
    except (ExpertiseStateError, ExpertiseAccessError, InvalidExpertiseError, UploadError) as error:
        raise_for_flow_error(error)

    expert = await users.get_by_id(updated.expert_id) if updated.expert_id else None
    if expert is not None:
        background_tasks.add_task(send_revision_letter, updated, expert)

    return await to_schema(updated, users, payments)


@router.post("/{expertise_id}/conclusion")
async def send_conclusion(
    background_tasks: BackgroundTasks,
    result: str = Form(..., description="Исход: positive, negative или remarks"),
    files: list[UploadFile] = File(default=[], description="Подписанное заключение и файлы ЭЦП"),
    expertise: Expertise = Depends(get_visible_expertise),
    expert: User = Depends(require_expert),
    usecase: SendConclusionUseCase = Depends(get_send_conclusion_usecase),
    users: UserRepository = Depends(get_user_repository),
    payments: PaymentRepository = Depends(get_payment_repository),
) -> ExpertiseOutSchema:
    """Шаг 10: эксперт отправляет подписанное заключение заказчику."""

    try:
        updated = await usecase.execute(expert, expertise, result, files)
    except (ExpertiseStateError, ExpertiseAccessError, InvalidExpertiseError, UploadError) as error:
        raise_for_flow_error(error)

    customer = await users.get_by_id(updated.customer_id)
    if customer is not None:
        background_tasks.add_task(send_conclusion_sent_letter, updated, customer)

    return await to_schema(updated, users, payments)


@router.post("/{expertise_id}/accept-work")
async def accept_work(
    background_tasks: BackgroundTasks,
    expertise: Expertise = Depends(get_visible_expertise),
    customer: User = Depends(require_customer),
    usecase: AcceptWorkUseCase = Depends(get_accept_work_usecase),
    users: UserRepository = Depends(get_user_repository),
    payments: PaymentRepository = Depends(get_payment_repository),
) -> ExpertiseOutSchema:
    """Шаг 12: заказчик принял работу."""

    try:
        updated = await usecase.execute(customer, expertise)
    except (ExpertiseStateError, ExpertiseAccessError) as error:
        raise_for_flow_error(error)

    expert = await users.get_by_id(updated.expert_id) if updated.expert_id else None
    if expert is not None:
        background_tasks.add_task(send_work_accepted_letter, updated, expert)

    return await to_schema(updated, users, payments)


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
