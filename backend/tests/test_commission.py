"""Заявки кандидатов в конкурсную комиссию."""

import asyncio
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.models.commission import CommissionApplication
from app.schemas.commission import CommissionApplicationInSchema
from app.services.commission.letter import build_html, build_text
from app.services.commission.usecases.create_application import (
    CreateCommissionApplicationUseCase,
)
from app.services.experts.exceptions import InvalidCertificateError


class FakeCommissionRepository:
    def __init__(self) -> None:
        self.items: list[CommissionApplication] = []

    async def add(self, application: CommissionApplication) -> CommissionApplication:
        application.id = len(self.items) + 1
        application.created_at = datetime(2026, 10, 1, 9, 30, tzinfo=timezone.utc)
        self.items.append(application)
        return application


def make_payload(attestations: list[dict], full_name: str = "Иванов Иван Иванович") -> CommissionApplicationInSchema:
    return CommissionApplicationInSchema(
        full_name=full_name,
        phone="+7 913 000-00-00",
        email="expert@example.com",
        attestations=attestations,
    )


def test_create_application_keeps_attestations() -> None:
    repo = FakeCommissionRepository()
    usecase = CreateCommissionApplicationUseCase(repo)

    payload = make_payload(
        [
            {"area_code": "Э1", "object_code": "kl_tp", "category": 1},
            {"area_code": "Э13", "object_code": "d", "category": 2},
        ]
    )
    application = asyncio.run(usecase.execute(payload))

    assert application.full_name == "Иванов Иван Иванович"
    assert application.phone == "+7 913 000-00-00"
    assert application.email == "expert@example.com"
    assert application.attestations == [
        {"area_code": "Э1", "object_code": "kl_tp", "category": 1},
        {"area_code": "Э13", "object_code": "d", "category": 2},
    ]
    assert repo.items == [application]


def test_create_application_rejects_unknown_area_and_object() -> None:
    usecase = CreateCommissionApplicationUseCase(FakeCommissionRepository())

    with pytest.raises(InvalidCertificateError):
        asyncio.run(usecase.execute(make_payload([{"area_code": "Э12", "object_code": "d", "category": 1}])))

    with pytest.raises(InvalidCertificateError):
        asyncio.run(usecase.execute(make_payload([{"area_code": "Э99", "object_code": "ob", "category": 1}])))


def test_schema_requires_attestation_and_category_range() -> None:
    with pytest.raises(ValidationError):
        make_payload([])

    with pytest.raises(ValidationError):
        make_payload([{"area_code": "Э1", "object_code": "ob", "category": 4}])


def test_letter_lists_attestations() -> None:
    application = CommissionApplication(
        id=7,
        full_name="Петров Пётр",
        phone="+7 913 111-11-11",
        email="petrov@example.com",
        attestations=[{"area_code": "Э1", "object_code": "kl_tp", "category": 1}],
    )
    application.created_at = datetime(2026, 10, 1, 9, 30, tzinfo=timezone.utc)

    assert "Э1 КЛ/ТП, 1 категория" in build_text(application)
    assert "petrov@example.com" in build_text(application)
    assert "Заявка №7 в конкурсную комиссию" in build_html(application)
