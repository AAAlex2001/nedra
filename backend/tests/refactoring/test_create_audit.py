"""Подача заявок на аудит."""

from io import BytesIO
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker
from starlette.datastructures import Headers, UploadFile

from src.audit.enums import AuditStatus
from src.audit.exceptions import InvalidAuditApplicationError
from src.audit.models.audit import Audit
from src.audit.models.audit_application import AuditApplication
from src.audit.models.audit_company import AuditCompany
from src.audit.models.audit_document import AuditDocument
from src.audit.site.audit_upload_files import AuditUploadFiles
from src.audit.site.request_dependencies import get_create_audit_usecase
from src.audit.site.schemas.create_audit import CreateAuditRequest
from src.contracts.models.contract import Contract
from src.core.file_exceptions import InvalidUploadError
from src.core.settings import Settings
from src.notifications.models.notification import Notification
from src.users.models.user import User


async def test_create_audit_saves_separate_entities(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
    audit_payload: CreateAuditRequest,
    tmp_path: Path,
) -> None:
    """Сохранить заявку, аудит, анкету, договор и реквизиты."""

    _, customer_id, lead_id = audit_ids
    settings.private_dir = tmp_path
    async with session_factory() as session:
        customer = await session.get(User, customer_id)
        usecase = get_create_audit_usecase(session=session, settings=settings)
        result = await usecase.execute(
            user=customer, payload=audit_payload, files=AuditUploadFiles()
        )

    async with session_factory() as session:
        request = await session.get(Audit, result.id)
        audit = await session.get(Audit, result.id)
        application = await session.get(AuditApplication, result.id)
        company = await session.get(AuditCompany, result.id)
        contract = await session.scalar(select(Contract).where(Contract.audit_id == result.id))
        notification = await session.scalar(select(Notification))

        assert request.customer_id == customer_id
        assert audit.status == AuditStatus.NEW
        assert audit.customer_budget == audit_payload.price
        assert audit.agreed_price is None
        assert application.details["scope"] == "one"
        assert application.object_name == "Котельная (А01-12345-0001)"
        assert company.inn == audit_payload.company.inn
        assert audit.customer_type == "legal"
        assert contract.kind == "audit"
        assert notification.user_id == lead_id
        assert notification.audit_id == result.id


async def test_bad_second_file_rolls_back_request_and_removes_first_file(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
    audit_payload: CreateAuditRequest,
    tmp_path: Path,
) -> None:
    """Откатить заявку и файлы при ошибке второй загрузки."""

    _, customer_id, _ = audit_ids
    settings.private_dir = tmp_path
    valid_file = UploadFile(
        filename="document.pdf",
        file=BytesIO(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF\n"),
        headers=Headers({"content-type": "application/pdf"}),
    )
    invalid_file = UploadFile(
        filename="fake.pdf",
        file=BytesIO(b"<html>not a PDF</html>"),
        headers=Headers({"content-type": "application/pdf"}),
    )

    async with session_factory() as session:
        customer = await session.get(User, customer_id)
        usecase = get_create_audit_usecase(session=session, settings=settings)
        usecase.letters.sender.send = AsyncMock()

        with pytest.raises(InvalidUploadError):
            await usecase.execute(
                user=customer,
                payload=audit_payload,
                files=AuditUploadFiles(documents=[valid_file, invalid_file], item_numbers=[1, 2]),
            )

        usecase.letters.sender.send.assert_not_awaited()

    assert list((tmp_path / "expertise-documents").iterdir()) == []
    async with session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(Audit)) == 1


async def test_notification_failure_removes_files_and_request(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
    audit_payload: CreateAuditRequest,
    tmp_path: Path,
) -> None:
    """Откатить заявку и файлы при ошибке уведомления."""

    _, customer_id, _ = audit_ids
    settings.private_dir = tmp_path
    document = UploadFile(
        filename="document.pdf",
        file=BytesIO(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF\n"),
        headers=Headers({"content-type": "application/pdf"}),
    )

    async with session_factory() as session:
        customer = await session.get(User, customer_id)
        usecase = get_create_audit_usecase(session=session, settings=settings)
        usecase.notifications.add_many = AsyncMock(side_effect=RuntimeError("Ошибка уведомления"))
        usecase.letters.sender.send = AsyncMock()

        with pytest.raises(RuntimeError, match="Ошибка уведомления"):
            await usecase.execute(
                user=customer,
                payload=audit_payload,
                files=AuditUploadFiles(documents=[document], item_numbers=[1]),
            )

        usecase.letters.sender.send.assert_not_awaited()

    assert list((tmp_path / "expertise-documents").iterdir()) == []
    async with session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(Audit)) == 1
        assert await session.scalar(select(func.count()).select_from(AuditDocument)) == 0
        assert await session.scalar(select(func.count()).select_from(Notification)) == 0


async def test_unknown_commit_result_keeps_files(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
    audit_payload: CreateAuditRequest,
    tmp_path: Path,
) -> None:
    """Сохранить файлы при неизвестном результате commit."""

    _, customer_id, _ = audit_ids
    settings.private_dir = tmp_path
    document = UploadFile(
        filename="document.pdf",
        file=BytesIO(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF\n"),
        headers=Headers({"content-type": "application/pdf"}),
    )

    async with session_factory() as session:
        customer = await session.get(User, customer_id)
        usecase = get_create_audit_usecase(session=session, settings=settings)
        commit = session.commit

        async def commit_then_disconnect() -> None:
            """Имитировать потерю соединения после commit."""

            await commit()
            raise ConnectionError("Соединение потеряно")

        session.commit = AsyncMock(side_effect=commit_then_disconnect)
        usecase.letters.sender.send = AsyncMock()

        with pytest.raises(ConnectionError, match="Соединение потеряно"):
            await usecase.execute(
                user=customer,
                payload=audit_payload,
                files=AuditUploadFiles(documents=[document], item_numbers=[1]),
            )

        usecase.letters.sender.send.assert_not_awaited()

    async with session_factory() as session:
        saved_document = await session.scalar(select(AuditDocument))
        assert saved_document is not None
        assert (tmp_path / saved_document.file_path).is_file()
        assert await session.scalar(select(func.count()).select_from(Audit)) == 2
        assert await session.scalar(select(func.count()).select_from(AuditDocument)) == 1
        assert await session.scalar(select(func.count()).select_from(Notification)) == 1


async def test_consultation_notifies_managers_only(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
    audit_payload: CreateAuditRequest,
    tmp_path: Path,
) -> None:
    """Отправить заявку на консультацию менеджерам."""

    _, customer_id, _ = audit_ids
    settings.private_dir = tmp_path
    settings.notify_emails = ["manager@example.com"]
    audit_payload.details.params.kind = "consultation"

    async with session_factory() as session:
        customer = await session.get(User, customer_id)
        usecase = get_create_audit_usecase(session=session, settings=settings)
        usecase.letters.sender.send = AsyncMock()
        result = await usecase.execute(
            user=customer, payload=audit_payload, files=AuditUploadFiles()
        )

        assert result.status == AuditStatus.CONSULTATION
        usecase.letters.sender.send.assert_awaited_once()
        assert usecase.letters.sender.send.call_args.kwargs["recipient"] == "manager@example.com"

    async with session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(Notification)) == 0


@pytest.mark.parametrize("missing_file", ["power_of_attorney", "sto_file"])
async def test_required_attachment_is_checked_before_saving(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
    audit_payload: CreateAuditRequest,
    tmp_path: Path,
    missing_file: str,
) -> None:
    """Проверить обязательные приложения до сохранения заявки."""

    _, customer_id, _ = audit_ids
    settings.private_dir = tmp_path
    if missing_file == "power_of_attorney":
        audit_payload.details.applicant.by_proxy = True
    else:
        audit_payload.details.params.use_sto = True
        audit_payload.details.params.sto_name = "Стандарт организации"

    async with session_factory() as session:
        customer = await session.get(User, customer_id)
        usecase = get_create_audit_usecase(session=session, settings=settings)

        with pytest.raises(InvalidAuditApplicationError):
            await usecase.execute(user=customer, payload=audit_payload, files=AuditUploadFiles())

        assert await session.scalar(select(func.count()).select_from(Audit)) == 1
