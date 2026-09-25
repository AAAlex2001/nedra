"""Тесты экспертизы без БД и без диска: подача, путь по шагам, платежи."""

import asyncio
from datetime import date, datetime, timezone
from decimal import Decimal
from io import BytesIO

import docx

import pytest

from app.models.expert import ExpertCertificate
from app.models.expertise import ContractKind, Expertise, ExpertiseResult, ExpertiseStatus
from app.models.notification import Notification
from app.models.payment import Payment, PaymentStatus
from app.models.tariff import Tariff
from app.models.user import User, UserRole
from app.schemas.expertise import ExpertiseCompanyInSchema, ExpertiseInSchema
from app.services.contracts.document import (
    CONTRACT,
    NDA,
    all_paragraphs,
    build_signed_document,
    contract_problem,
    initials,
    working_days,
)
from app.services.contracts.executors import NEDRA, SIBNTC, executor_for
from app.services.contracts.kinds import resolve_kind
from app.services.expertise.access import can_view
from app.services.expertise.exceptions import (
    ExpertiseAccessError,
    ExpertiseStateError,
    InvalidExpertiseError,
    PriceMissingError,
)
from app.services.expertise.money import split_price
from app.services.expertise.repo import certificate_fits
from app.services.expertise.usecases.accept_expertise import AcceptExpertiseUseCase
from app.services.expertise.usecases.accept_work import AcceptWorkUseCase
from app.services.expertise.usecases.apply_expertise_payment import ApplyExpertisePaymentUseCase
from app.services.expertise.usecases.confirm_expertise import ConfirmExpertiseUseCase
from app.services.expertise.usecases.create_expertise import CreateExpertiseUseCase, build_company
from app.services.expertise.usecases.create_expertise_payment import CreateExpertisePaymentUseCase
from app.services.expertise.usecases.mark_conclusion_ready import MarkConclusionReadyUseCase
from app.services.expertise.usecases.resubmit_documentation import ResubmitDocumentationUseCase
from app.services.expertise.usecases.send_conclusion import SendConclusionUseCase
from app.services.expertise.usecases.send_remarks import SendRemarksUseCase
from app.services.expertise.validators import resolve_category, validate_pair
from app.services.files.storage import StoredFile


class FakeExpertiseRepository:
    def __init__(self) -> None:
        self.items: list[Expertise] = []

    async def add(self, expertise: Expertise) -> Expertise:
        expertise.id = len(self.items) + 1
        self.items.append(expertise)
        return expertise

    async def save(self, expertise: Expertise) -> Expertise:
        return expertise

    async def get_by_payment_id(self, payment_id: int) -> Expertise | None:
        for item in self.items:
            if payment_id in (item.advance_payment_id, item.final_payment_id):
                return item
        return None


class FakeProfileRepository:
    def __init__(self, experts: list[User], certificates: list[ExpertCertificate] | None = None) -> None:
        self.experts = experts
        self.certificates = certificates or []

    async def list_certified(self, object_code: str, area_code: str, max_category: int) -> list[User]:
        return self.experts

    async def list_certificates(self, user_id: int) -> list[ExpertCertificate]:
        return self.certificates


class FakeNotificationRepository:
    def __init__(self) -> None:
        self.added: list[Notification] = []

    def add_all(self, notifications: list[Notification]) -> None:
        self.added.extend(notifications)


class FakeTariffRepository:
    def __init__(self, price: Decimal | None) -> None:
        self.price = price

    async def get(self, area_code: str, object_code: str) -> Tariff | None:
        if self.price is None:
            return None
        return Tariff(area_code=area_code, object_code=object_code, price=self.price)


class FakePaymentRepository:
    def __init__(self) -> None:
        self.items: list[Payment] = []

    async def get_by_id(self, payment_id: int) -> Payment | None:
        for item in self.items:
            if item.id == payment_id:
                return item
        return None


class FakeCreatePayment:
    def __init__(self, payments: FakePaymentRepository) -> None:
        self.payments = payments
        self.calls: list[tuple[Decimal, str]] = []

    async def execute(self, user: User, amount: Decimal, description: str) -> Payment:
        self.calls.append((amount, description))
        payment = Payment(
            user_id=user.id,
            amount=amount,
            description=description,
            status=PaymentStatus.PENDING,
            provider_payment_id=f"yk-{len(self.payments.items) + 1}",
            confirmation_url="https://yookassa.ru/pay",
        )
        payment.id = len(self.payments.items) + 1
        self.payments.items.append(payment)
        return payment


class FakeStorage:
    def __init__(self) -> None:
        self.written: list[bytes] = []

    async def save(self, file, folder: str, max_size_bytes: int, allowed_types=None) -> StoredFile:
        return StoredFile(
            path=f"{folder}/fake.pdf",
            original_name=file.name,
            size=100,
            content_type="application/pdf",
        )

    def save_bytes(
        self, content: bytes, folder: str, original_name: str, content_type: str, extension: str
    ) -> StoredFile:
        self.written.append(content)
        return StoredFile(
            path=f"{folder}/fake{extension}",
            original_name=original_name,
            size=len(content),
            content_type=content_type,
        )


class FakeUpload:
    def __init__(self, name: str) -> None:
        self.name = name


def make_user(user_id: int, role: UserRole) -> User:
    user = User(email=f"u{user_id}@example.com", password_hash="x", full_name="Имя", phone="+79990000000", role=role)
    user.id = user_id
    return user


def make_usecase(
    experts: list[User], price: Decimal | None = Decimal("20000")
) -> tuple[CreateExpertiseUseCase, FakeExpertiseRepository, FakeNotificationRepository]:
    expertises = FakeExpertiseRepository()
    notifications = FakeNotificationRepository()
    usecase = CreateExpertiseUseCase(
        expertises, FakeProfileRepository(experts), notifications, FakeTariffRepository(price), FakeStorage()
    )
    return usecase, expertises, notifications


FITTING = [ExpertCertificate(area_code="Э4", object_code="kl", category=1, valid_until=date(2030, 1, 1))]

COMPANY = ExpertiseCompanyInSchema(
    full_name="Общество с ограниченной ответственностью «Ромашка»",
    name="ООО «Ромашка»",
    inn="5401 234567",
    kpp="540101001",
    ogrn="1025400000000",
    address="630000, г. Новосибирск, ул. Ленина, 1",
    bank="АО «Альфа-Банк»",
    bic="045004774",
    account="4070 2810 0000 0000 0001",
    corr_account="30101810600000000774",
    signer_position="Генеральный директор",
    signer_name="Иванов Иван Иванович",
    signer_genitive="генерального директора Иванова Ивана Ивановича",
)


def make_order(**fields) -> ExpertiseInSchema:
    return ExpertiseInSchema(object_name="Проект консервации шахты", company=COMPANY, **fields)


def make_expertise(status: ExpertiseStatus, price: Decimal | None = Decimal("20001")) -> Expertise:
    expertise = Expertise(
        customer_id=1, object_code="kl", area_code="Э4", expert_category=2, status=status, price=price
    )
    expertise.id = 1
    return expertise


def make_contract_ready(kind: ContractKind) -> Expertise:
    expertise = make_expertise(ExpertiseStatus.EXPERT_READY)
    expertise.expert_id = 10
    expertise.contract_kind = kind
    expertise.object_name = "Проект консервации шахты"
    expertise.deadline = "three_days"
    expertise.company = build_company(COMPANY)
    return expertise


def test_resolve_category_prefers_hazard_class() -> None:
    assert resolve_category(1, None) == 1
    assert resolve_category(2, None) == 2
    assert resolve_category(4, None) == 3
    assert resolve_category(4, 1) == 3
    assert resolve_category(None, 2) == 2

    assert resolve_category(None, None) is None

    with pytest.raises(InvalidExpertiseError):
        resolve_category(None, 5)


def test_validate_pair() -> None:
    validate_pair("kl_tp", "Э1")
    validate_pair("kl", "Э4")

    with pytest.raises(InvalidExpertiseError):
        validate_pair("kl", "Э1")

    with pytest.raises(InvalidExpertiseError):
        validate_pair("d", "Э1")


def test_split_price_puts_kopeck_into_final() -> None:
    assert split_price(Decimal("20000")) == (Decimal("10000.00"), Decimal("10000.00"))
    assert split_price(Decimal("20001")) == (Decimal("10000.50"), Decimal("10000.50"))
    assert split_price(Decimal("0.03")) == (Decimal("0.02"), Decimal("0.01"))


def test_create_saves_documents_price_and_notifies_experts() -> None:
    expert = make_user(10, UserRole.EXPERT)
    usecase, expertises, notifications = make_usecase([expert])
    customer = make_user(1, UserRole.CUSTOMER)
    data = make_order(object_code="kl_tp", area_code="Э1", hazard_class=2, comment="  срочно ")

    created = asyncio.run(usecase.execute(customer, data, [FakeUpload("a.pdf"), FakeUpload("b.pdf")]))

    expertise = created.expertise
    assert expertise.id == 1
    assert expertise.customer_id == 1
    assert expertise.expert_category == 2
    assert expertise.comment == "срочно"
    assert expertise.status == ExpertiseStatus.NEW
    assert expertise.price == Decimal("20000")
    assert len(expertise.documents) == 2
    assert expertise.documents[0].original_name == "a.pdf"
    assert created.notified_experts == [expert]
    assert len(notifications.added) == 1
    assert notifications.added[0].user_id == 10


def test_create_without_tariff_keeps_price_empty() -> None:
    usecase, expertises, notifications = make_usecase([], price=None)
    data = make_order(object_code="kl_tp", area_code="Э1", expert_category=1)

    created = asyncio.run(usecase.execute(make_user(1, UserRole.CUSTOMER), data, [FakeUpload("a.pdf")]))

    assert created.expertise.price is None


def test_create_without_known_fields_keeps_them_empty() -> None:
    expert = make_user(10, UserRole.EXPERT)
    usecase, expertises, notifications = make_usecase([expert])
    data = make_order(deadline="three_days", comment="не знаю, что нужно")

    created = asyncio.run(
        usecase.execute(make_user(1, UserRole.CUSTOMER), data, [FakeUpload("a.pdf")])
    )

    expertise = created.expertise
    assert expertise.object_code is None
    assert expertise.area_code is None
    assert expertise.expert_category is None
    assert expertise.deadline == "three_days"
    assert expertise.price is None
    assert created.notified_experts == [expert]


def test_create_saves_company_card_separately() -> None:
    usecase, expertises, notifications = make_usecase([])
    data = make_order(object_code="kl_tp", area_code="Э1", expert_category=1)

    created = asyncio.run(
        usecase.execute(
            make_user(1, UserRole.CUSTOMER),
            data,
            [FakeUpload("a.pdf")],
            FakeUpload("card.docx"),
        )
    )

    kinds = [document.kind for document in created.expertise.documents]
    assert kinds == ["documentation", "company_card"]


def test_certificate_fits_when_request_has_no_area() -> None:
    expertise = Expertise(customer_id=1, object_code=None, area_code=None, expert_category=None)
    certificate = ExpertCertificate(object_code="d", area_code="Э4", category=3)

    assert certificate_fits([certificate], expertise) is True


def test_create_requires_files() -> None:
    usecase, expertises, notifications = make_usecase([])
    data = make_order(object_code="kl_tp", area_code="Э1", expert_category=1)

    with pytest.raises(InvalidExpertiseError):
        asyncio.run(usecase.execute(make_user(1, UserRole.CUSTOMER), data, []))


def test_certificate_fits_by_category() -> None:
    expertise = Expertise(customer_id=1, object_code="d", area_code="Э4", expert_category=2)
    strong = ExpertCertificate(area_code="Э4", object_code="d", category=1, valid_until=date(2030, 1, 1))
    weak = ExpertCertificate(area_code="Э4", object_code="d", category=3, valid_until=date(2030, 1, 1))
    other = ExpertCertificate(area_code="Э5", object_code="d", category=1, valid_until=date(2030, 1, 1))

    assert certificate_fits([strong], expertise)
    assert not certificate_fits([weak], expertise)
    assert not certificate_fits([other], expertise)


def test_can_view_rules() -> None:
    expertise = Expertise(customer_id=1, object_code="d", area_code="Э4", expert_category=2)
    owner = make_user(1, UserRole.CUSTOMER)
    stranger = make_user(2, UserRole.CUSTOMER)
    expert = make_user(10, UserRole.EXPERT)
    fitting = [ExpertCertificate(area_code="Э4", object_code="d", category=1, valid_until=date(2030, 1, 1))]

    assert can_view(expertise, owner, [])
    assert not can_view(expertise, stranger, [])
    assert can_view(expertise, expert, fitting)
    assert not can_view(expertise, expert, [])

    expertise.expert_id = 10
    assert can_view(expertise, expert, [])
    expertise.expert_id = 11
    assert not can_view(expertise, expert, fitting)


def test_accept_locks_expertise_and_notifies_customer() -> None:
    expertise = make_expertise(ExpertiseStatus.NEW)
    notifications = FakeNotificationRepository()
    usecase = AcceptExpertiseUseCase(
        FakeExpertiseRepository(), FakeProfileRepository([], FITTING), notifications
    )
    expert = make_user(10, UserRole.EXPERT)

    with pytest.raises(InvalidExpertiseError):
        asyncio.run(usecase.execute(expert, expertise))

    with pytest.raises(InvalidExpertiseError):
        asyncio.run(usecase.execute(expert, expertise, ContractKind.DECLARATION))

    updated = asyncio.run(usecase.execute(expert, expertise, ContractKind.LIQUIDATION))

    assert updated.status == ExpertiseStatus.EXPERT_READY
    assert updated.expert_id == 10
    assert updated.expert_ready_at is not None
    assert updated.contract_kind == ContractKind.LIQUIDATION
    assert notifications.added[0].user_id == 1

    with pytest.raises(ExpertiseStateError):
        asyncio.run(usecase.execute(make_user(11, UserRole.EXPERT), expertise))


def test_accept_requires_fitting_certificate_and_price() -> None:
    expert = make_user(10, UserRole.EXPERT)

    no_certificates = AcceptExpertiseUseCase(
        FakeExpertiseRepository(), FakeProfileRepository([], []), FakeNotificationRepository()
    )
    with pytest.raises(ExpertiseAccessError):
        asyncio.run(no_certificates.execute(expert, make_expertise(ExpertiseStatus.NEW)))

    no_price = AcceptExpertiseUseCase(
        FakeExpertiseRepository(), FakeProfileRepository([], FITTING), FakeNotificationRepository()
    )
    with pytest.raises(PriceMissingError):
        asyncio.run(no_price.execute(expert, make_expertise(ExpertiseStatus.NEW, price=None)))


def test_confirm_signs_contract_and_notifies_expert() -> None:
    expertise = make_contract_ready(ContractKind.DECLARATION)
    notifications = FakeNotificationRepository()
    storage = FakeStorage()
    usecase = ConfirmExpertiseUseCase(FakeExpertiseRepository(), notifications, storage)

    with pytest.raises(ExpertiseAccessError):
        asyncio.run(usecase.execute(make_user(2, UserRole.CUSTOMER), expertise))

    updated = asyncio.run(usecase.execute(make_user(1, UserRole.CUSTOMER), expertise))

    assert updated.status == ExpertiseStatus.CONTRACT
    assert updated.contract_at is not None
    assert [item.kind for item in updated.documents] == ["contract", "nda"]
    assert updated.documents[0].original_name.startswith("Договор БЭ-")
    assert updated.documents[1].original_name.startswith("Соглашение о конфиденциальности БЭ-")
    assert len(storage.written) == 2
    assert notifications.added[0].user_id == 10

    with pytest.raises(ExpertiseStateError):
        asyncio.run(usecase.execute(make_user(1, UserRole.CUSTOMER), expertise))


def test_confirm_requires_company_and_contract_kind() -> None:
    usecase = ConfirmExpertiseUseCase(
        FakeExpertiseRepository(), FakeNotificationRepository(), FakeStorage()
    )
    customer = make_user(1, UserRole.CUSTOMER)

    without_company = make_contract_ready(ContractKind.DECLARATION)
    without_company.company = None
    with pytest.raises(ExpertiseStateError):
        asyncio.run(usecase.execute(customer, without_company))

    without_kind = make_contract_ready(ContractKind.DECLARATION)
    without_kind.contract_kind = None
    with pytest.raises(ExpertiseStateError):
        asyncio.run(usecase.execute(customer, without_kind))


def test_resolve_kind_by_object() -> None:
    assert resolve_kind("tp", None) == ContractKind.REEQUIPMENT
    assert resolve_kind("d", None) == ContractKind.DECLARATION
    assert resolve_kind("ob", None) == ContractKind.JUSTIFICATION
    assert resolve_kind("kl", None) is None
    assert resolve_kind(None, None) is None
    assert resolve_kind("kl", "liquidation") == ContractKind.LIQUIDATION
    assert resolve_kind("kl_tp", "reequipment") == ContractKind.REEQUIPMENT
    assert resolve_kind(None, "declaration") == ContractKind.DECLARATION

    with pytest.raises(InvalidExpertiseError):
        resolve_kind("kl", "reequipment")


def test_declaration_goes_to_sibntc() -> None:
    assert executor_for(ContractKind.DECLARATION) == SIBNTC
    assert executor_for(ContractKind.CONSERVATION) == NEDRA
    assert executor_for(None) == NEDRA


def signed_text(kind: str, expertise: Expertise) -> str:
    signed_at = datetime(2026, 9, 25, tzinfo=timezone.utc)
    content = build_signed_document(kind, expertise, make_user(1, UserRole.CUSTOMER), 7, signed_at)
    document = docx.Document(BytesIO(content))

    return "\n".join(paragraph.text for paragraph in all_paragraphs(document))


def test_contract_is_filled_from_expertise() -> None:
    expertise = make_contract_ready(ContractKind.CONSERVATION)
    assert contract_problem(expertise) is None

    text = signed_text(CONTRACT, expertise)

    assert "{{" not in text
    assert "Договор №БЭ-2026-0001" in text
    assert "«25» сентября 2026 г." in text
    assert "документации на консервацию ОПО «Проект консервации шахты»" in text
    assert "3 (три) рабочих дня" in text
    assert "20 001,00 (Двадцать тысяч один рубль 00 копеек)" in text
    assert "в т.ч. НДС 7% – 1 308,48" in text
    assert "ИНН/КПП 5401234567/540101001" in text
    assert "в лице генерального директора Иванова Ивана Ивановича" in text
    assert "И.И. Иванов" in text
    assert "ООО «НПИ «Недра»" in text


def test_nda_is_filled_for_executor() -> None:
    text = signed_text(NDA, make_contract_ready(ContractKind.DECLARATION))

    assert "{{" not in text
    assert "К ДОГОВОРУ № БЭ-2026-0001 ОТ «25» СЕНТЯБРЯ 2026 Г." in text
    assert "договора № БЭ-2026-0001 от «25» сентября 2026 г." in text
    assert "в лице генерального директора Иванова Ивана Ивановича" in text
    assert "технических устройств «Проект консервации шахты»" in text
    assert "Электронная почта: u1@example.com" in text
    assert "Телефон: +79990000000" in text
    assert "/И.И. Иванов/" in text
    assert "ООО «СибНТЦ «Промтехэксперт»" in text


def test_contract_helpers() -> None:
    assert initials("Иванов Иван Иванович") == "И.И. Иванов"
    assert initials("Иванов") == "Иванов"
    assert working_days("today") == "1 (один) рабочий день"
    assert working_days(None) == "5 (пять) рабочих дней"


def test_create_resolves_kind_and_saves_company() -> None:
    usecase, expertises, notifications = make_usecase([])

    created = asyncio.run(
        usecase.execute(make_user(1, UserRole.CUSTOMER), make_order(object_code="tp"), [FakeUpload("a.pdf")])
    )

    expertise = created.expertise
    assert expertise.contract_kind == ContractKind.REEQUIPMENT
    assert expertise.object_name == "Проект консервации шахты"
    assert expertise.company is not None
    assert expertise.company.inn == "5401234567"
    assert expertise.company.account == "40702810000000000001"
    assert expertise.company.signer_basis == "Устава"


def test_card_payment_is_closed_for_declaration() -> None:
    expertise = make_expertise(ExpertiseStatus.CONTRACT)
    expertise.contract_kind = ContractKind.DECLARATION
    payments = FakePaymentRepository()
    usecase = CreateExpertisePaymentUseCase(
        FakeExpertiseRepository(), payments, FakeCreatePayment(payments)
    )

    with pytest.raises(ExpertiseStateError):
        asyncio.run(usecase.execute(make_user(1, UserRole.CUSTOMER), expertise))


def test_payment_stage_amounts_and_reuse() -> None:
    expertise = make_expertise(ExpertiseStatus.CONTRACT)
    expertise.expert_id = 10
    payments = FakePaymentRepository()
    create_payment = FakeCreatePayment(payments)
    usecase = CreateExpertisePaymentUseCase(FakeExpertiseRepository(), payments, create_payment)
    customer = make_user(1, UserRole.CUSTOMER)

    advance = asyncio.run(usecase.execute(customer, expertise))

    assert advance.amount == Decimal("10000.50")
    assert expertise.advance_payment_id == advance.id
    assert "аванс" in create_payment.calls[0][1]

    again = asyncio.run(usecase.execute(customer, expertise))
    assert again.id == advance.id
    assert len(create_payment.calls) == 1

    expertise.status = ExpertiseStatus.CONCLUSION_READY
    final = asyncio.run(usecase.execute(customer, expertise))

    assert final.amount == Decimal("10000.50")
    assert expertise.final_payment_id == final.id
    assert "остаток" in create_payment.calls[1][1]

    expertise.status = ExpertiseStatus.IN_PROGRESS
    with pytest.raises(ExpertiseStateError):
        asyncio.run(usecase.execute(customer, expertise))


def test_apply_payment_moves_status_once() -> None:
    expertise = make_expertise(ExpertiseStatus.CONTRACT)
    expertise.expert_id = 10
    expertise.advance_payment_id = 5
    expertises = FakeExpertiseRepository()
    expertises.items.append(expertise)
    notifications = FakeNotificationRepository()
    usecase = ApplyExpertisePaymentUseCase(expertises, notifications)

    pending = Payment(user_id=1, amount=Decimal("1"), description="x", status=PaymentStatus.PENDING, provider_payment_id="a")
    pending.id = 5
    assert asyncio.run(usecase.execute(pending)) is None

    paid = Payment(user_id=1, amount=Decimal("1"), description="x", status=PaymentStatus.SUCCEEDED, provider_payment_id="a")
    paid.id = 5
    updated = asyncio.run(usecase.execute(paid))

    assert updated is not None
    assert updated.status == ExpertiseStatus.IN_PROGRESS
    assert updated.advance_paid_at is not None
    assert len(notifications.added) == 1

    asyncio.run(usecase.execute(paid))
    assert len(notifications.added) == 1

    expertise.status = ExpertiseStatus.CONCLUSION_READY
    expertise.final_payment_id = 6
    final = Payment(user_id=1, amount=Decimal("1"), description="x", status=PaymentStatus.SUCCEEDED, provider_payment_id="b")
    final.id = 6
    updated = asyncio.run(usecase.execute(final))

    assert updated is not None
    assert updated.status == ExpertiseStatus.PAID
    assert updated.final_paid_at is not None


def test_remarks_cycle_returns_expertise_to_work() -> None:
    expertise = make_expertise(ExpertiseStatus.IN_PROGRESS)
    expertise.expert_id = 10
    expert = make_user(10, UserRole.EXPERT)
    customer = make_user(1, UserRole.CUSTOMER)
    notifications = FakeNotificationRepository()
    repo = FakeExpertiseRepository()

    remarks = SendRemarksUseCase(repo, notifications, FakeStorage())
    revision = ResubmitDocumentationUseCase(repo, notifications, FakeStorage())

    with pytest.raises(ExpertiseAccessError):
        asyncio.run(remarks.execute(make_user(11, UserRole.EXPERT), expertise, "текст", []))

    with pytest.raises(InvalidExpertiseError):
        asyncio.run(remarks.execute(expert, expertise, "   ", []))

    asyncio.run(remarks.execute(expert, expertise, "  Уточните раздел 3  ", [FakeUpload("r.pdf")]))

    assert expertise.status == ExpertiseStatus.REMARKS
    assert len(expertise.remarks) == 1
    assert expertise.remarks[0].text == "Уточните раздел 3"
    assert expertise.remarks[0].documents[0].kind == "remarks"
    assert notifications.added[0].user_id == 1

    with pytest.raises(InvalidExpertiseError):
        asyncio.run(revision.execute(customer, expertise, None, []))

    asyncio.run(revision.execute(customer, expertise, "  Исправил раздел 3  ", [FakeUpload("fixed.pdf")]))

    assert expertise.status == ExpertiseStatus.IN_PROGRESS
    assert expertise.remarks[0].resolved_at is not None
    assert expertise.remarks[0].response_text == "Исправил раздел 3"
    assert expertise.documents[-1].kind == "revision"
    assert expertise.remarks[0].documents[-1].kind == "revision"
    assert notifications.added[1].user_id == 10

    with pytest.raises(ExpertiseStateError):
        asyncio.run(revision.execute(customer, expertise, None, [FakeUpload("again.pdf")]))

    asyncio.run(remarks.execute(expert, expertise, None, [FakeUpload("r2.pdf")]))

    assert len(expertise.remarks) == 2
    assert expertise.remarks[1].text is None


def test_conclusion_ready_send_and_accept_work() -> None:
    expertise = make_expertise(ExpertiseStatus.IN_PROGRESS)
    expertise.expert_id = 10
    expert = make_user(10, UserRole.EXPERT)
    customer = make_user(1, UserRole.CUSTOMER)
    notifications = FakeNotificationRepository()
    repo = FakeExpertiseRepository()

    ready = MarkConclusionReadyUseCase(repo, notifications)
    with pytest.raises(ExpertiseAccessError):
        asyncio.run(ready.execute(make_user(11, UserRole.EXPERT), expertise))
    asyncio.run(ready.execute(expert, expertise))
    assert expertise.status == ExpertiseStatus.CONCLUSION_READY

    send = SendConclusionUseCase(repo, notifications, FakeStorage())
    with pytest.raises(ExpertiseStateError):
        asyncio.run(send.execute(expert, expertise, ExpertiseResult.POSITIVE, [FakeUpload("c.pdf")]))

    expertise.status = ExpertiseStatus.PAID
    with pytest.raises(InvalidExpertiseError):
        asyncio.run(send.execute(expert, expertise, "weird", [FakeUpload("c.pdf")]))
    with pytest.raises(InvalidExpertiseError):
        asyncio.run(send.execute(expert, expertise, ExpertiseResult.POSITIVE, []))

    asyncio.run(send.execute(expert, expertise, ExpertiseResult.NEGATIVE, [FakeUpload("c.pdf")]))
    assert expertise.status == ExpertiseStatus.SENT
    assert expertise.result == ExpertiseResult.NEGATIVE
    assert expertise.documents[0].kind == "conclusion"

    accept = AcceptWorkUseCase(repo, notifications)
    asyncio.run(accept.execute(customer, expertise))
    assert expertise.status == ExpertiseStatus.ACCEPTED
    assert expertise.accepted_at is not None

    recipients = [item.user_id for item in notifications.added]
    assert recipients == [1, 1, 10]
