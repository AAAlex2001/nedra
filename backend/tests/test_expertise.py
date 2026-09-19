"""Тесты подачи экспертизы без БД и без диска."""

import asyncio
from datetime import date

import pytest

from app.models.expert import ExpertCertificate
from app.models.expertise import Expertise, ExpertiseStatus
from app.models.notification import Notification
from app.models.user import User, UserRole
from app.schemas.expertise import ExpertiseInSchema
from app.services.expertise.access import can_view
from app.services.expertise.exceptions import InvalidExpertiseError
from app.services.expertise.repo import certificate_fits
from app.services.expertise.usecases.create_expertise import CreateExpertiseUseCase
from app.services.expertise.validators import resolve_category, validate_pair
from app.services.files.storage import StoredFile


class FakeExpertiseRepository:
    def __init__(self) -> None:
        self.items: list[Expertise] = []

    async def add(self, expertise: Expertise) -> Expertise:
        expertise.id = len(self.items) + 1
        self.items.append(expertise)
        return expertise


class FakeProfileRepository:
    def __init__(self, experts: list[User]) -> None:
        self.experts = experts
        self.calls: list[tuple[str, str, int]] = []

    async def list_certified(self, object_code: str, area_code: str, max_category: int) -> list[User]:
        self.calls.append((object_code, area_code, max_category))
        return self.experts


class FakeNotificationRepository:
    def __init__(self) -> None:
        self.added: list[Notification] = []

    def add_all(self, notifications: list[Notification]) -> None:
        self.added.extend(notifications)


class FakeStorage:
    async def save(self, file, folder: str, max_size_bytes: int) -> StoredFile:
        return StoredFile(
            path=f"{folder}/fake.pdf",
            original_name=file.name,
            size=100,
            content_type="application/pdf",
        )


class FakeUpload:
    def __init__(self, name: str) -> None:
        self.name = name


def make_user(user_id: int, role: UserRole) -> User:
    user = User(email=f"u{user_id}@example.com", password_hash="x", full_name="Имя", phone="+79990000000", role=role)
    user.id = user_id
    return user


def make_usecase(experts: list[User]) -> tuple[CreateExpertiseUseCase, FakeExpertiseRepository, FakeNotificationRepository]:
    expertises = FakeExpertiseRepository()
    notifications = FakeNotificationRepository()
    usecase = CreateExpertiseUseCase(
        expertises, FakeProfileRepository(experts), notifications, FakeStorage()
    )
    return usecase, expertises, notifications


def test_resolve_category_prefers_hazard_class() -> None:
    assert resolve_category(1, None) == 1
    assert resolve_category(2, None) == 2
    assert resolve_category(4, None) == 3
    assert resolve_category(4, 1) == 3
    assert resolve_category(None, 2) == 2

    with pytest.raises(InvalidExpertiseError):
        resolve_category(None, None)

    with pytest.raises(InvalidExpertiseError):
        resolve_category(None, 5)


def test_validate_pair() -> None:
    validate_pair("kl_tp", "Э1")
    validate_pair("kl", "Э4")

    with pytest.raises(InvalidExpertiseError):
        validate_pair("kl", "Э1")

    with pytest.raises(InvalidExpertiseError):
        validate_pair("d", "Э1")


def test_create_saves_documents_and_notifies_experts() -> None:
    expert = make_user(10, UserRole.EXPERT)
    usecase, expertises, notifications = make_usecase([expert])
    customer = make_user(1, UserRole.CUSTOMER)
    data = ExpertiseInSchema(object_code="kl_tp", area_code="Э1", hazard_class=2, comment="  срочно ")

    created = asyncio.run(usecase.execute(customer, data, [FakeUpload("a.pdf"), FakeUpload("b.pdf")]))

    expertise = created.expertise
    assert expertise.id == 1
    assert expertise.customer_id == 1
    assert expertise.expert_category == 2
    assert expertise.comment == "срочно"
    assert expertise.status == ExpertiseStatus.NEW
    assert len(expertise.documents) == 2
    assert expertise.documents[0].original_name == "a.pdf"
    assert created.notified_experts == [expert]
    assert len(notifications.added) == 1
    assert notifications.added[0].user_id == 10


def test_create_requires_files() -> None:
    usecase, expertises, notifications = make_usecase([])
    data = ExpertiseInSchema(object_code="kl_tp", area_code="Э1", expert_category=1)

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
