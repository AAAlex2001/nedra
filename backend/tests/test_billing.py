"""Тесты счетов и печатных документов без БД и без диска."""

import asyncio
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.models.billing import CustomerCompany, Invoice, InvoiceStage
from app.models.expertise import Expertise, ExpertiseStatus
from app.models.notification import Notification
from app.models.user import User, UserRole
from app.routers.billing import pdf_response
from app.schemas.billing import CompanyInSchema
from app.services.billing.exceptions import (
    CompanyRequiredError,
    InvalidCompanyError,
    InvoiceAlreadyPaidError,
    InvoiceNotFoundError,
)
from app.services.billing.usecases.confirm_invoice import ConfirmInvoiceUseCase
from app.services.billing.usecases.issue_invoice import IssueInvoiceUseCase
from app.services.billing.usecases.report_payment import ReportInvoicePaidUseCase
from app.services.billing.usecases.save_company import SaveCustomerCompanyUseCase
from app.services.billing.validators import normalize_inn, normalize_kpp
from app.services.files.storage import StoredFile
from app.services.documents.act_pdf import build_act_pdf
from app.services.documents.company import CompanyRequisites
from app.services.documents.fonts import register_fonts
from app.services.documents.invoice_pdf import build_invoice_pdf
from app.services.documents.layout import amount_in_words, format_amount, vat_included, vat_text
from app.services.expertise.exceptions import ExpertiseStateError, PriceMissingError
from app.services.expertise.stages import current_stage, mark_stage_paid


class FakeCompanyRepository:
    def __init__(self, company: CustomerCompany | None = None) -> None:
        self.company = company

    async def get_by_user(self, user_id: int) -> CustomerCompany | None:
        return self.company

    async def save(self, company: CustomerCompany) -> CustomerCompany:
        self.company = company
        return company


class FakeInvoiceRepository:
    def __init__(self) -> None:
        self.items: list[Invoice] = []

    async def get_by_id(self, invoice_id: int) -> Invoice | None:
        for item in self.items:
            if item.id == invoice_id:
                return item
        return None

    async def get_unpaid_for_stage(self, expertise_id: int, stage: str) -> Invoice | None:
        for item in self.items:
            if item.expertise_id == expertise_id and item.stage == stage and item.paid_at is None:
                return item
        return None

    async def add(self, invoice: Invoice) -> Invoice:
        invoice.id = len(self.items) + 1
        invoice.created_at = datetime.now(timezone.utc)
        self.items.append(invoice)
        return invoice

    async def save(self, invoice: Invoice) -> Invoice:
        return invoice


class FakeExpertiseRepository:
    def __init__(self, expertise: Expertise) -> None:
        self.expertise = expertise

    async def get_by_id(self, expertise_id: int) -> Expertise | None:
        return self.expertise if self.expertise.id == expertise_id else None

    async def save(self, expertise: Expertise) -> Expertise:
        return expertise


class FakeStorage:
    async def save(self, file, folder: str, max_size_bytes: int, allowed_types=None) -> StoredFile:
        return StoredFile(
            path=f"{folder}/fake.pdf",
            original_name=file.name,
            size=100,
            content_type="application/pdf",
        )


class FakeUpload:
    def __init__(self, name: str) -> None:
        self.name = name


class FakeNotificationRepository:
    def __init__(self) -> None:
        self.added: list[Notification] = []

    def add_all(self, notifications: list[Notification]) -> None:
        self.added.extend(notifications)


def make_customer() -> User:
    user = User(email="c@example.com", password_hash="x", full_name="Заказчик", phone="+79990000000", role=UserRole.CUSTOMER)
    user.id = 1
    return user


def make_company() -> CustomerCompany:
    return CustomerCompany(
        user_id=1, name="ООО «Ромашка»", inn="7701234567", kpp="770101001", address="Москва"
    )


def make_expertise(status: ExpertiseStatus, price: Decimal | None = Decimal("20000")) -> Expertise:
    expertise = Expertise(
        customer_id=1,
        expert_id=10,
        object_code="kl",
        area_code="Р­4",
        expert_category=2,
        status=status,
        price=price,
    )
    expertise.id = 1
    return expertise


def test_normalize_requisites() -> None:
    assert normalize_inn("77 0123 4567") == "7701234567"
    assert normalize_inn("770123456789") == "770123456789"
    assert normalize_kpp(" 770101001 ") == "770101001"
    assert normalize_kpp("  ") is None
    assert normalize_kpp(None) is None

    with pytest.raises(InvalidCompanyError):
        normalize_inn("123")

    with pytest.raises(InvalidCompanyError):
        normalize_kpp("12345")


def test_save_company_normalizes() -> None:
    repo = FakeCompanyRepository()
    usecase = SaveCustomerCompanyUseCase(repo)
    data = CompanyInSchema(
        name="  ООО «Ромашка» ", inn="77 0123 4567", kpp="770101001", address=" Москва "
    )

    company = asyncio.run(usecase.execute(make_customer(), data))

    assert company.name == "ООО «Ромашка»"
    assert company.inn == "7701234567"
    assert company.address == "Москва"


def test_issue_invoice_splits_amount_and_reuses_unpaid() -> None:
    invoices = FakeInvoiceRepository()
    usecase = IssueInvoiceUseCase(invoices, FakeCompanyRepository(make_company()))
    expertise = make_expertise(ExpertiseStatus.CONTRACT)
    customer = make_customer()

    invoice = asyncio.run(usecase.execute(customer, expertise))

    assert invoice.amount == Decimal("10000.00")
    assert invoice.stage == InvoiceStage.ADVANCE
    assert invoice.payer_name == "ООО «Ромашка»"

    again = asyncio.run(usecase.execute(customer, expertise))
    assert again.id == invoice.id
    assert len(invoices.items) == 1

    expertise.status = ExpertiseStatus.CONCLUSION_READY
    final = asyncio.run(usecase.execute(customer, expertise))
    assert final.stage == InvoiceStage.FINAL
    assert final.amount == Decimal("10000.00")


def test_issue_invoice_requires_company_price_and_stage() -> None:
    invoices = FakeInvoiceRepository()
    customer = make_customer()

    without_company = IssueInvoiceUseCase(invoices, FakeCompanyRepository())
    with pytest.raises(CompanyRequiredError):
        asyncio.run(without_company.execute(customer, make_expertise(ExpertiseStatus.CONTRACT)))

    usecase = IssueInvoiceUseCase(invoices, FakeCompanyRepository(make_company()))

    with pytest.raises(PriceMissingError):
        asyncio.run(usecase.execute(customer, make_expertise(ExpertiseStatus.CONTRACT, None)))

    with pytest.raises(ExpertiseStateError):
        asyncio.run(usecase.execute(customer, make_expertise(ExpertiseStatus.IN_PROGRESS)))


def test_confirm_invoice_moves_expertise_once() -> None:
    invoices = FakeInvoiceRepository()
    expertise = make_expertise(ExpertiseStatus.CONTRACT)
    notifications = FakeNotificationRepository()
    issue = IssueInvoiceUseCase(invoices, FakeCompanyRepository(make_company()))
    invoice = asyncio.run(issue.execute(make_customer(), expertise))

    confirm = ConfirmInvoiceUseCase(
        invoices, FakeExpertiseRepository(expertise), notifications
    )
    paid = asyncio.run(confirm.execute(invoice.id))

    assert paid.paid_at is not None
    assert expertise.status == ExpertiseStatus.IN_PROGRESS
    assert expertise.advance_paid_at is not None
    assert notifications.added[0].user_id == 10

    with pytest.raises(InvoiceAlreadyPaidError):
        asyncio.run(confirm.execute(invoice.id))

    with pytest.raises(InvoiceNotFoundError):
        asyncio.run(confirm.execute(99))


def test_stage_helpers() -> None:
    assert current_stage(make_expertise(ExpertiseStatus.CONTRACT)) == InvoiceStage.ADVANCE
    assert current_stage(make_expertise(ExpertiseStatus.CONCLUSION_READY)) == InvoiceStage.FINAL
    assert current_stage(make_expertise(ExpertiseStatus.SENT)) is None

    expertise = make_expertise(ExpertiseStatus.IN_PROGRESS)
    assert mark_stage_paid(expertise, InvoiceStage.ADVANCE) is None
    assert expertise.status == ExpertiseStatus.IN_PROGRESS


def test_documents_build_pdf() -> None:
    try:
        register_fonts()
    except FileNotFoundError:
        pytest.skip("на этой машине нет шрифта с кириллицей")

    company = CompanyRequisites(
        name="РћРћРћ В«РќРџР В«РќРµРґСЂР°В»",
        inn="5400000000",
        kpp="540001001",
        address="Новосибирск",
        bank="Банк",
        bic="040000000",
        account="40702810000000000000",
        corr_account="30101810000000000000",
        director="РРІР°РЅРѕРІ Р. Р.",
        vat_rate=7,
    )
    expertise = make_expertise(ExpertiseStatus.ACCEPTED)
    expertise.created_at = datetime.now(timezone.utc)
    expertise.accepted_at = datetime.now(timezone.utc)

    invoice = Invoice(
        expertise_id=1,
        stage=InvoiceStage.ADVANCE,
        amount=Decimal("10000.00"),
        payer_name="ООО «Ромашка»",
        payer_inn="7701234567",
        payer_kpp="770101001",
        payer_address="Москва",
    )
    invoice.id = 1
    invoice.created_at = datetime.now(timezone.utc)

    assert build_invoice_pdf(invoice, "Аванс 50%", company).startswith(b"%PDF")
    assert build_act_pdf(expertise, make_company(), "Экспертиза", company).startswith(b"%PDF")


def test_money_words_and_format() -> None:
    assert format_amount(Decimal("20000.00")) == "20 000,00"
    assert format_amount(Decimal("10000.50")) == "10 000,50"
    assert amount_in_words(Decimal("20000.00")) == "Двадцать тысяч рублей 00 копеек"
    assert amount_in_words(Decimal("1234.56")) == (
        "Одна тысяча двести тридцать четыре рубля 56 копеек"
    )
    assert amount_in_words(Decimal("0.01")) == "Ноль рублей 01 копейка"


def test_customer_reports_payment_once() -> None:
    expertise = make_expertise(ExpertiseStatus.CONTRACT)
    invoices = FakeInvoiceRepository()
    customer = make_customer()

    issue = IssueInvoiceUseCase(invoices, FakeCompanyRepository(make_company()))
    invoice = asyncio.run(issue.execute(customer, expertise))

    usecase = ReportInvoicePaidUseCase(
        invoices, FakeExpertiseRepository(expertise), FakeStorage(), FakeNotificationRepository()
    )

    with pytest.raises(InvoiceNotFoundError):
        asyncio.run(usecase.execute(customer, 404))

    reported = asyncio.run(usecase.execute(customer, invoice.id))
    assert reported.reported_at is not None

    first = reported.reported_at
    again = asyncio.run(usecase.execute(customer, invoice.id))
    assert again.reported_at == first


def test_customer_attaches_guarantee_letter() -> None:
    expertise = make_expertise(ExpertiseStatus.CONTRACT)
    invoices = FakeInvoiceRepository()
    customer = make_customer()

    issue = IssueInvoiceUseCase(invoices, FakeCompanyRepository(make_company()))
    invoice = asyncio.run(issue.execute(customer, expertise))

    usecase = ReportInvoicePaidUseCase(
        invoices, FakeExpertiseRepository(expertise), FakeStorage(), FakeNotificationRepository()
    )

    asyncio.run(
        usecase.execute(customer, invoice.id, FakeUpload("letter.pdf"), "guarantee_letter")
    )

    attached = expertise.documents[-1]
    assert attached.kind == "guarantee_letter"
    assert attached.original_name == "letter.pdf"


def test_payment_document_kind_defaults_to_payment_order() -> None:
    expertise = make_expertise(ExpertiseStatus.CONTRACT)
    invoices = FakeInvoiceRepository()
    customer = make_customer()

    issue = IssueInvoiceUseCase(invoices, FakeCompanyRepository(make_company()))
    invoice = asyncio.run(issue.execute(customer, expertise))

    usecase = ReportInvoicePaidUseCase(
        invoices, FakeExpertiseRepository(expertise), FakeStorage(), FakeNotificationRepository()
    )

    asyncio.run(usecase.execute(customer, invoice.id, FakeUpload("order.pdf"), "что-то своё"))

    assert expertise.documents[-1].kind == "payment_order"

    invoice.paid_at = datetime.now(timezone.utc)
    with pytest.raises(InvoiceAlreadyPaidError):
        asyncio.run(usecase.execute(customer, invoice.id))


def test_pdf_filename_survives_http_headers() -> None:
    response = pdf_response(b"%PDF", "Счёт 2026-0001.pdf")
    disposition = response.headers["content-disposition"]

    assert disposition == "attachment; filename*=UTF-8''%D0%A1%D1%87%D1%91%D1%82%202026-0001.pdf"


def test_vat_is_included_in_price() -> None:
    assert vat_included(Decimal("20000.00"), 7) == Decimal("1308.41")
    assert vat_included(Decimal("12000.00"), 20) == Decimal("2000.00")
    assert vat_included(Decimal("20000.00"), 0) == Decimal("0")

    assert vat_text(Decimal("20000.00"), 7) == "В том числе НДС 7 % — 1 308,41"
    assert vat_text(Decimal("20000.00"), 0) == "Без НДС"

