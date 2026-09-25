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
    ContactsRequiredError,
    ExpertNotFoundError,
    InvalidCertificateError,
    InvalidDirectionError,
)
from app.services.experts.usecases.approve_application import ApproveExpertApplicationUseCase
from app.services.experts.usecases.delete_expert import DeleteExpertUseCase
from app.services.experts.usecases.reject_application import RejectExpertApplicationUseCase
from app.services.experts.usecases.submit_application import SubmitExpertApplicationUseCase
from app.services.experts.validators import validate_certificate, validate_directions
from app.services.users.exceptions import EmailAlreadyTakenError


class FakeUserRepository:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}
        self.next_id = 1

    async def get_by_email(self, email: str) -> User | None:
        return self.users.get(email)

    async def get_by_id(self, user_id: int) -> User | None:
        for user in self.users.values():
            if user.id == user_id:
                return user
        return None

    async def save(self, user: User) -> User:
        return user

    async def delete(self, user: User) -> None:
        del self.users[user.email]

    def put(self, user: User) -> User:
        user.id = self.next_id
        self.next_id = self.next_id + 1
        self.users[user.email] = user
        return user


class FakeProfileRepository:
    def __init__(self) -> None:
        self.profiles: dict[int, ExpertProfile] = {}
        self.removed: list[int] = []

    async def get_by_user(self, user_id: int) -> ExpertProfile | None:
        return self.profiles.get(user_id)

    async def remove(self, profile: ExpertProfile) -> None:
        self.removed.append(profile.user_id)
        del self.profiles[profile.user_id]


class FakeApplicationRepository:
    def __init__(self, users: FakeUserRepository, profiles: FakeProfileRepository) -> None:
        self.items: list[ExpertApplication] = []
        self.users = users
        self.profiles = profiles

    async def get_by_id(self, application_id: int) -> ExpertApplication | None:
        for item in self.items:
            if item.id == application_id:
                return item
        return None

    async def get_by_user_id(self, user_id: int) -> ExpertApplication | None:
        for item in self.items:
            if item.user_id == user_id:
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
        if user.id is None:
            self.users.put(user)
        profile.user_id = user.id
        self.profiles.profiles[user.id] = profile
        for certificate in application.certificates:
            certificate.user_id = user.id
        application.user_id = user.id
        return application


class World:
    """Все фейковые репозитории вместе, чтобы сценарии видели одни и те же данные."""

    def __init__(self) -> None:
        self.users = FakeUserRepository()
        self.profiles = FakeProfileRepository()
        self.applications = FakeApplicationRepository(self.users, self.profiles)

    def submit(self) -> SubmitExpertApplicationUseCase:
        return SubmitExpertApplicationUseCase(self.applications, self.users)

    def approve(self) -> ApproveExpertApplicationUseCase:
        return ApproveExpertApplicationUseCase(self.applications, self.users)

    def delete_expert(self) -> DeleteExpertUseCase:
        return DeleteExpertUseCase(self.users, self.applications, self.profiles)


def make_payload(email: str | None = "Expert@Example.com") -> ExpertApplicationInSchema:
    return ExpertApplicationInSchema(
        email=email,
        password="secret123" if email else None,
        full_name=" Пётр Экспертов " if email else None,
        phone="+7 (999) 111-22-33" if email else None,
        directions=["industrial_safety", "sms_audit"],
        certificates=[
            CertificateInSchema(
                area_code="Э1",
                object_code="kl_tp",
                category=2,
                valid_until=date(2028, 1, 1),
                number=" 77-ЭПБ-12345 ",
            )
        ],
    )


def make_customer(world: World, email: str = "customer@example.com") -> User:
    user = User(email=email, password_hash="hash", full_name="Заказчик", phone="+79990000000", role=UserRole.CUSTOMER)
    return world.users.put(user)


def test_validate_certificate_combinations() -> None:
    validate_certificate("Э4", "kl", 1)
    validate_certificate("Э1", "kl_tp", 3)
    validate_certificate("Э2", "d", 2)

    with pytest.raises(InvalidCertificateError):
        validate_certificate("Э1", "d", 1)

    with pytest.raises(InvalidCertificateError):
        validate_certificate("Э1", "tp", 1)

    with pytest.raises(InvalidCertificateError):
        validate_certificate("Э4", "kl_tp", 1)

    with pytest.raises(InvalidCertificateError):
        validate_certificate("Э4", "tu", 1)


def test_validate_directions() -> None:
    validate_directions(["ecology", "design"])

    with pytest.raises(InvalidDirectionError):
        validate_directions(["ecology", "ecology"])

    with pytest.raises(InvalidDirectionError):
        validate_directions(["unknown"])


def test_submit_creates_pending_application() -> None:
    world = World()

    application = asyncio.run(world.submit().execute(make_payload()))

    assert application.id == 1
    assert application.email == "expert@example.com"
    assert application.full_name == "Пётр Экспертов"
    assert application.phone == "+79991112233"
    assert application.status == ApplicationStatus.PENDING
    assert application.user_id is None
    assert application.password_hash != "secret123"
    assert len(application.certificates) == 1
    assert application.certificates[0].number == "77-ЭПБ-12345"


def test_submit_requires_contacts() -> None:
    world = World()

    with pytest.raises(ContactsRequiredError):
        asyncio.run(world.submit().execute(make_payload(email=None)))


def test_submit_rejects_existing_account_email() -> None:
    world = World()
    make_customer(world, "expert@example.com")

    with pytest.raises(EmailAlreadyTakenError):
        asyncio.run(world.submit().execute(make_payload()))


def test_submit_rejects_second_pending_application() -> None:
    world = World()
    asyncio.run(world.submit().execute(make_payload()))

    with pytest.raises(ApplicationAlreadyPendingError):
        asyncio.run(world.submit().execute(make_payload("expert@example.com")))


def test_submit_requires_certificate_number() -> None:
    world = World()
    payload = make_payload()
    payload.certificates[0].number = "   "

    with pytest.raises(InvalidCertificateError):
        asyncio.run(world.submit().execute(payload))


def test_approve_creates_expert_account() -> None:
    world = World()
    asyncio.run(world.submit().execute(make_payload()))

    application = asyncio.run(world.approve().execute(1))

    user = world.users.users["expert@example.com"]
    assert application.status == ApplicationStatus.APPROVED
    assert application.user_id == user.id
    assert user.role == UserRole.EXPERT
    assert user.password_hash == application.password_hash
    assert world.profiles.profiles[user.id].directions == ["industrial_safety", "sms_audit"]
    assert application.certificates[0].user_id == user.id

    with pytest.raises(ApplicationAlreadyReviewedError):
        asyncio.run(world.approve().execute(1))


def test_approve_rejects_taken_email() -> None:
    world = World()
    asyncio.run(world.submit().execute(make_payload()))
    make_customer(world, "expert@example.com")

    with pytest.raises(EmailAlreadyTakenError):
        asyncio.run(world.approve().execute(1))


def test_delete_expert_removes_account() -> None:
    world = World()
    asyncio.run(world.submit().execute(make_payload()))
    asyncio.run(world.approve().execute(1))
    user = world.users.users["expert@example.com"]

    asyncio.run(world.delete_expert().execute(user.id))

    application = world.applications.items[0]
    assert world.profiles.removed == [user.id]
    assert "expert@example.com" not in world.users.users
    assert application.status == ApplicationStatus.REJECTED
    assert application.user_id is None
    assert application.admin_comment == "Профиль эксперта удалён администратором"

    with pytest.raises(ExpertNotFoundError):
        asyncio.run(world.delete_expert().execute(user.id))


def test_reject_stores_comment() -> None:
    world = World()
    asyncio.run(world.submit().execute(make_payload()))
    usecase = RejectExpertApplicationUseCase(world.applications)

    application = asyncio.run(usecase.execute(1, "  Удостоверение просрочено "))

    assert application.status == ApplicationStatus.REJECTED
    assert application.admin_comment == "Удостоверение просрочено"
    assert application.reviewed_at is not None
