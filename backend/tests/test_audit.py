"""Тесты Блиц-аудита: подача по перечню, видимость для аудиторов, договор и отчёт о документах."""

import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from io import BytesIO

import docx
import pytest

from app.models.expertise import (
    ContractKind,
    CustomerType,
    Expertise,
    ExpertiseDocument,
    ExpertiseStatus,
    ServiceKind,
)
from app.models.user import UserRole
from app.schemas.audit import AuditInSchema
from app.services.audit.checklist import AUDIT_DOCUMENTS
from app.services.audit.report import build_documents_report
from app.services.audit.usecases.create_audit import CreateAuditUseCase
from app.services.contracts.document import CONTRACT, contract_number
from app.services.contracts.executors import NEDRA_AUDIT, executor_for
from app.services.contracts.kinds import allowed_kinds
from app.services.expertise.access import can_view
from app.services.expertise.exceptions import ExpertiseAccessError, InvalidExpertiseError
from app.services.expertise.repo import executor_fits
from app.services.expertise.usecases.accept_expertise import AcceptExpertiseUseCase
from app.services.expertise.usecases.send_conclusion import SendConclusionUseCase
from app.services.expertise.usecases.create_expertise import build_company
from test_expertise import (
    COMPANY,
    FITTING,
    FakeExpertiseRepository,
    FakeNotificationRepository,
    FakeProfileRepository,
    FakeStorage,
    FakeUpload,
    make_user,
    signed_text,
)


def make_audit_order() -> AuditInSchema:
    return AuditInSchema(object_name="ООО «Ромашка», сеть газопотребления", price=Decimal("90000"), company=COMPANY)


def make_audit(status: ExpertiseStatus) -> Expertise:
    audit = Expertise(
        customer_id=1,
        service=ServiceKind.AUDIT,
        contract_kind=ContractKind.AUDIT,
        object_name="ООО «Ромашка», сеть газопотребления",
        status=status,
        price=Decimal("90000"),
        customer_type=CustomerType.LEGAL,
    )
    audit.id = 7
    return audit


def test_create_audit_keeps_items_and_notifies_auditors() -> None:
    auditor = make_user(20, UserRole.EXPERT)
    expertises = FakeExpertiseRepository()
    notifications = FakeNotificationRepository()
    usecase = CreateAuditUseCase(
        expertises, FakeProfileRepository([], auditors=[auditor]), notifications, FakeStorage()
    )

    files = [FakeUpload("устав.pdf"), FakeUpload("лицензия.pdf"), FakeUpload("лицензия-2.pdf")]
    created = asyncio.run(usecase.execute(make_user(1, UserRole.CUSTOMER), make_audit_order(), files, [1, 3, 3]))

    audit = created.expertise
    assert audit.service == ServiceKind.AUDIT
    assert audit.contract_kind == ContractKind.AUDIT
    assert [item.item_number for item in audit.documents] == [1, 3, 3]
    assert {item.kind for item in audit.documents} == {"audit_item"}
    assert created.notified_experts == [auditor]
    assert notifications.added[0].user_id == 20


def test_create_audit_checks_item_numbers() -> None:
    usecase = CreateAuditUseCase(
        FakeExpertiseRepository(), FakeProfileRepository([]), FakeNotificationRepository(), FakeStorage()
    )
    customer = make_user(1, UserRole.CUSTOMER)

    with pytest.raises(InvalidExpertiseError):
        asyncio.run(usecase.execute(customer, make_audit_order(), [FakeUpload("a.pdf")], [48]))

    with pytest.raises(InvalidExpertiseError):
        asyncio.run(usecase.execute(customer, make_audit_order(), [FakeUpload("a.pdf")], []))

    with pytest.raises(InvalidExpertiseError):
        asyncio.run(usecase.execute(customer, make_audit_order(), [], []))


def test_audit_is_visible_only_to_auditors() -> None:
    audit = make_audit(ExpertiseStatus.NEW)
    expert = make_user(10, UserRole.EXPERT)

    assert executor_fits(audit, [], True)
    assert not executor_fits(audit, FITTING, False)
    assert can_view(audit, expert, [], True)
    assert not can_view(audit, expert, FITTING, False)


def test_accept_audit_requires_audit_direction() -> None:
    auditor = make_user(20, UserRole.EXPERT)
    expert = make_user(10, UserRole.EXPERT)
    profiles = FakeProfileRepository([], FITTING, auditors=[auditor])
    usecase = AcceptExpertiseUseCase(FakeExpertiseRepository(), profiles, FakeNotificationRepository())

    with pytest.raises(ExpertiseAccessError):
        asyncio.run(usecase.execute(expert, make_audit(ExpertiseStatus.NEW)))

    accepted = asyncio.run(usecase.execute(auditor, make_audit(ExpertiseStatus.NEW)))
    assert accepted.status == ExpertiseStatus.EXPERT_READY
    assert accepted.contract_kind == ContractKind.AUDIT


def test_audit_contract_uses_own_template_and_number() -> None:
    audit = make_audit(ExpertiseStatus.EXPERT_READY)
    audit.expert_id = 20
    audit.deadline = "week"
    audit.company = build_company(COMPANY)

    signed_at = datetime(2026, 10, 6, tzinfo=timezone.utc)

    assert executor_for(ContractKind.AUDIT) == NEDRA_AUDIT
    assert contract_number(audit, signed_at) == "БА-2026-0007"
    assert ContractKind.AUDIT not in allowed_kinds(None)

    text = signed_text(CONTRACT, audit)
    assert "аудита системы управления промышленной безопасностью" in text
    assert "ООО «Ромашка», сеть газопотребления" in text


def test_send_audit_report_without_result() -> None:
    audit = make_audit(ExpertiseStatus.PAID)
    audit.expert_id = 20
    usecase = SendConclusionUseCase(FakeExpertiseRepository(), FakeNotificationRepository(), FakeStorage())

    sent = asyncio.run(usecase.execute(make_user(20, UserRole.EXPERT), audit, None, [FakeUpload("отчёт.pdf")]))

    assert sent.status == ExpertiseStatus.SENT
    assert sent.result is None


def test_documents_report_counts_provided_items() -> None:
    audit = make_audit(ExpertiseStatus.NEW)
    audit.company = build_company(COMPANY)
    audit.documents = [
        ExpertiseDocument(kind="audit_item", item_number=1, uploaded_by=1, file_path="x", original_name="устав.pdf", size=1, content_type="application/pdf"),
        ExpertiseDocument(kind="audit_item", item_number=4, uploaded_by=1, file_path="x", original_name="свидетельство.pdf", size=1, content_type="application/pdf"),
    ]

    content = build_documents_report(audit, datetime(2026, 10, 6, 12, 0, tzinfo=timezone.utc))
    document = docx.Document(BytesIO(content))
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)

    assert f"по 2 из {len(AUDIT_DOCUMENTS)} пунктов" in text
    table = document.tables[0]
    assert len(table.rows) == len(AUDIT_DOCUMENTS) + 1
    assert table.rows[1].cells[2].text == "Представлен"
    assert table.rows[1].cells[3].text == "устав.pdf"
    assert table.rows[2].cells[2].text == "Не представлен"
