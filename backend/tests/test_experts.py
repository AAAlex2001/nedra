"""Тесты справочника аттестации и сценариев заявок экспертов без БД."""

import asyncio
from datetime import date

import pytest

from app.models.expert import ApplicationStatus, ExpertApplication, ExpertProfile
from app.models.user import User, UserRole
from app.schemas.expert import CertificateInSchema, ExpertApplicationInSchema
from app.services.experts.exceptions import (
    ApplicationAlreadyPendingError,
    ApplicationAlreadyReviewedError,
    InvalidCertificateError,
    InvalidDirectionError,
)
from app.services.experts.usecases.approve_application import ApproveExpertApplicationUseCase
from app.services.experts.usecases.reject_application import RejectExpertApplicationUseCase
from app.services.experts.usecases.submit_application import SubmitExpertApplicationUseCase
from app.services.experts.validators import validate_certificate, validate_directions
from app.services.users.exceptions import EmailAlreadyTakenError


class FakeUserRepository:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}

    async def get_by_email(self, email: str) -> User | None:
        return self.users.get(email)


class FakeApplicationRepository:
    def __init__(self) -> None:
        self.items: list[ExpertApplication] = []
        self.approved: list[tuple[ExpertApplication, User, ExpertProfile]] = []

    async def get_by_id(self, application_id: int) -> ExpertApplication | None:
        for item in self.items:
            if item.id == application_id:
                return item
        return None

    async def has_pending(self, email: str) -> bool:
        for item in self.items:
            if item.email == email and item.status == ApplicationStatus.PENDING:
                return True
        return False

    async def add(self, application: ExpertApplication) -> ExpertApplication:
        application.id = len(self.items) + 1
        self.items.append(application)
        return application

    async def save(self, application: ExpertApplication) -> ExpertApplication:
        return application

    async def approve(
        self, application: ExpertApplication, user: User, profile: ExpertProfile
    ) -> ExpertApplication:
        user.id = 100 + application.id
        profile.user_id = user.id
        for certificate in application.certificates:
            certificate.user_id = user.id
        application.user_id = user.id
        self.approved.append((application, user, profile))
        return application


class FakeStorage:
    async def save(self, file, folder: str):
        raise AssertionError("в тестах сканы не загружаются")


def make_payload(email: str = "Expert@Example.com") -> ExpertApplicationInSchema:
    return ExpertApplicationInSchema(
        email=email,
        password="secret123",
        full_name=" Пётр Экспертов ",
        phone="+7 (999) 111-22-33",
        directions=["industrial_safety", "sms_audit"],
        certificates=[
            CertificateInSchema(
                area_code="Э1", object_code="kl_tp", category=2, valid_until=date(2028, 1, 1)
            )
        ],
    )


def make_usecase(
    applications: FakeApplicationRepository, users: FakeUserRepository | None = None
) -> SubmitExpertApplicationUseCase:
    return SubmitExpertApplicationUseCase(applications, users or FakeUserRepository(), FakeStorage())


def test_validate_certificate_combinations() -> None:
    validate_certificate("Э4", "kl", 1)
    validate_certificate("Э1", "kl_tp", 3)

    with pytest.raises(InvalidCertificateError):
        validate_certificate("Э1", "kl", 1)

    with pytest.raises(InvalidCertificateError):
        validate_certificate("Э1", "d", 1)

    with pytest.raises(InvalidCertificateError):
        validate_certificate("Э99", "tu", 1)

    with pytest.raises(InvalidCertificateError):
        validate_certificate("Э2", "d", 4)


def test_validate_directions() -> None:
    validate_directions(["ecology", "design"])

    with pytest.raises(InvalidDirectionError):
        validate_directions(["ecology", "ecology"])

    with pytest.raises(InvalidDirectionError):
        validate_directions(["unknown"])


def test_submit_creates_pending_application() -> None:
    applications = FakeApplicationRepository()
    usecase = make_usecase(applications)

    application = asyncio.run(usecase.execute(make_payload(), []))

    assert application.id == 1
    assert application.email == "expert@example.com"
    assert application.full_name == "Пётр Экспертов"
    assert application.phone == "+79991112233"
    assert application.status == ApplicationStatus.PENDING
    assert application.password_hash != "secret123"
    assert len(application.certificates) == 1
    assert application.certificates[0].scan_path is None


def test_submit_rejects_second_pending_application() -> None:
    applications = FakeApplicationRepository()
    usecase = make_usecase(applications)
    asyncio.run(usecase.execute(make_payload(), []))

    with pytest.raises(ApplicationAlreadyPendingError):
        asyncio.run(usecase.execute(make_payload("expert@example.com"), []))


def test_submit_rejects_taken_email() -> None:
    users = FakeUserRepository()
    users.users["expert@example.com"] = User(
        email="expert@example.com", password_hash="x", full_name="x", phone="x", role=UserRole.CUSTOMER
    )
    usecase = make_usecase(FakeApplicationRepository(), users)

    with pytest.raises(EmailAlreadyTakenError):
        asyncio.run(usecase.execute(make_payload(), []))


def test_submit_rejects_missing_scan() -> None:
    payload = make_payload()
    payload.certificates[0].scan_index = 0
    usecase = make_usecase(FakeApplicationRepository())

    with pytest.raises(InvalidCertificateError):
        asyncio.run(usecase.execute(payload, []))


def test_approve_creates_expert_user() -> None:
    applications = FakeApplicationRepository()
    users = FakeUserRepository()
    asyncio.run(make_usecase(applications, users).execute(make_payload(), []))
    usecase = ApproveExpertApplicationUseCase(applications, users)

    application = asyncio.run(usecase.execute(1))

    assert application.status == ApplicationStatus.APPROVED
    assert application.reviewed_at is not None
    assert application.user_id == 101
    approved_application, user, profile = applications.approved[0]
    assert user.role == UserRole.EXPERT
    assert user.password_hash == application.password_hash
    assert profile.directions == ["industrial_safety", "sms_audit"]
    assert application.certificates[0].user_id == 101

    with pytest.raises(ApplicationAlreadyReviewedError):
        asyncio.run(usecase.execute(1))


def test_reject_stores_comment() -> None:
    applications = FakeApplicationRepository()
    asyncio.run(make_usecase(applications).execute(make_payload(), []))
    usecase = RejectExpertApplicationUseCase(applications)

    application = asyncio.run(usecase.execute(1, "  Удостоверение просрочено "))

    assert application.status == ApplicationStatus.REJECTED
    assert application.admin_comment == "Удостоверение просрочено"
    assert application.reviewed_at is not None
