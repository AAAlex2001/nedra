"""Счета и акты для заказчика: реквизиты, выставление счёта, печать PDF."""

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.dependencies.billing import (
    get_company_repository,
    get_invoice_repository,
    get_issue_invoice_usecase,
    get_save_company_usecase,
)
from app.dependencies.expertise import get_expertise_repository, get_visible_expertise
from app.dependencies.users import require_customer
from app.models.billing import Invoice, InvoiceStage
from app.models.expertise import Expertise, ExpertiseStatus
from app.models.user import User
from app.schemas.billing import (
    ActOutSchema,
    CompanyInSchema,
    CompanyOutSchema,
    InvoiceOutSchema,
)
from app.services.billing.exceptions import CompanyRequiredError, InvalidCompanyError
from app.services.billing.repo import CustomerCompanyRepository, InvoiceRepository
from app.services.billing.usecases.issue_invoice import IssueInvoiceUseCase
from app.services.billing.usecases.save_company import SaveCustomerCompanyUseCase
from app.services.documents.act_pdf import act_filename, act_number, build_act_pdf
from app.services.documents.company import (
    CompanyRequisitesMissingError,
    load_requisites,
)
from app.services.documents.invoice_pdf import (
    build_invoice_pdf,
    invoice_filename,
    invoice_number,
    stage_subject,
)
from app.services.experts.catalog import AREA_BY_CODE, OBJECT_BY_CODE
from app.services.expertise.exceptions import (
    ExpertiseAccessError,
    ExpertiseStateError,
    PriceMissingError,
)
from app.services.expertise.repo import ExpertiseRepository
from app.services.expertise.stages import STAGE_TITLES

router = APIRouter(tags=["billing"])

PDF_MEDIA_TYPE = "application/pdf"


def describe_expertise(expertise: Expertise) -> str:
    """Предмет работ для счёта и акта."""

    object_title = OBJECT_BY_CODE[expertise.object_code].title
    area = AREA_BY_CODE[expertise.area_code]

    return f"{object_title}, область аттестации {area.code}"


def to_invoice_schema(invoice: Invoice) -> InvoiceOutSchema:
    """Счёт наружу вместе с человеческим номером."""

    return InvoiceOutSchema(
        id=invoice.id,
        number=invoice_number(invoice),
        expertise_id=invoice.expertise_id,
        stage=InvoiceStage(invoice.stage),
        amount=invoice.amount,
        payer_name=invoice.payer_name,
        payer_inn=invoice.payer_inn,
        created_at=invoice.created_at,
        paid_at=invoice.paid_at,
    )


def pdf_response(content: bytes, filename: str) -> Response:
    """Отдать PDF на скачивание."""

    return Response(
        content=content,
        media_type=PDF_MEDIA_TYPE,
        headers={"Content-Disposition": f'attachment; filename*=UTF-8\'\'{filename}'},
    )


def load_company_requisites():
    """Наши реквизиты или понятная ошибка, если админ их не заполнил."""

    try:
        return load_requisites()
    except CompanyRequisitesMissingError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Реквизиты организации не настроены, обратитесь к администратору",
        ) from error


@router.get("/me/company")
async def get_company(
    customer: User = Depends(require_customer),
    companies: CustomerCompanyRepository = Depends(get_company_repository),
) -> CompanyOutSchema | None:
    """Реквизиты организации заказчика. Пусто, если он их ещё не заполнял."""

    company = await companies.get_by_user(customer.id)

    return CompanyOutSchema.model_validate(company) if company else None


@router.put("/me/company")
async def save_company(
    payload: CompanyInSchema,
    customer: User = Depends(require_customer),
    usecase: SaveCustomerCompanyUseCase = Depends(get_save_company_usecase),
) -> CompanyOutSchema:
    """Сохранить реквизиты организации: по ним выставляются счета и акты."""

    try:
        company = await usecase.execute(customer, payload)
    except InvalidCompanyError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error

    return CompanyOutSchema.model_validate(company)


@router.get("/invoices")
async def list_invoices(
    customer: User = Depends(require_customer),
    invoices: InvoiceRepository = Depends(get_invoice_repository),
) -> list[InvoiceOutSchema]:
    """Счета заказчика, новые первыми."""

    items = await invoices.list_for_customer(customer.id)

    return [to_invoice_schema(item) for item in items]


@router.post("/expertise/{expertise_id}/invoice", status_code=status.HTTP_201_CREATED)
async def issue_invoice(
    expertise: Expertise = Depends(get_visible_expertise),
    customer: User = Depends(require_customer),
    usecase: IssueInvoiceUseCase = Depends(get_issue_invoice_usecase),
) -> InvoiceOutSchema:
    """Выставить счёт на текущий этап оплаты."""

    try:
        invoice = await usecase.execute(customer, expertise)
    except ExpertiseAccessError as error:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(error)) from error
    except ExpertiseStateError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from error
    except (PriceMissingError, CompanyRequiredError) as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error

    return to_invoice_schema(invoice)


@router.get("/invoices/{invoice_id}/pdf")
async def download_invoice(
    invoice_id: int,
    customer: User = Depends(require_customer),
    invoices: InvoiceRepository = Depends(get_invoice_repository),
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
) -> Response:
    """Счёт в PDF. Чужой счёт выглядит как несуществующий."""

    invoice = await invoices.get_by_id(invoice_id)
    expertise = await expertises.get_by_id(invoice.expertise_id) if invoice else None

    if invoice is None or expertise is None or expertise.customer_id != customer.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Счёт не найден")

    company = load_company_requisites()
    subject = stage_subject(
        expertise.id,
        STAGE_TITLES[InvoiceStage(invoice.stage)],
        describe_expertise(expertise),
    )
    content = build_invoice_pdf(invoice, subject, company)

    return pdf_response(content, invoice_filename(invoice))


@router.get("/acts")
async def list_acts(
    customer: User = Depends(require_customer),
    expertises: ExpertiseRepository = Depends(get_expertise_repository),
) -> list[ActOutSchema]:
    """Акты по принятым работам. Отдельной таблицы нет: акт собирается из экспертизы."""

    items = await expertises.list_for_customer(customer.id)
    accepted = [item for item in items if item.status == ExpertiseStatus.ACCEPTED]

    return [
        ActOutSchema(
            expertise_id=item.id,
            number=act_number(item),
            amount=item.price,
            subject=describe_expertise(item),
            signed_at=item.accepted_at or item.created_at,
        )
        for item in accepted
    ]


@router.get("/acts/{expertise_id}/pdf")
async def download_act(
    expertise: Expertise = Depends(get_visible_expertise),
    customer: User = Depends(require_customer),
    companies: CustomerCompanyRepository = Depends(get_company_repository),
) -> Response:
    """Акт выполненных работ в PDF. Доступен после приёмки работы."""

    if expertise.customer_id != customer.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Акт не найден")

    if expertise.status != ExpertiseStatus.ACCEPTED:
        raise HTTPException(status.HTTP_409_CONFLICT, "Акт готовится после приёмки работы")

    payer = await companies.get_by_user(customer.id)
    if payer is None:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Заполните реквизиты организации в разделе «Мои данные»",
        )

    company = load_company_requisites()
    content = build_act_pdf(expertise, payer, describe_expertise(expertise), company)

    return pdf_response(content, act_filename(expertise))
