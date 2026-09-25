"""Тесты удостоверений эксперта в кабинете и админке без БД."""

import asyncio
from datetime import date

import pytest

from app.models.expert import ExpertCertificate
from app.schemas.expert import CertificateInSchema
from app.services.experts.exceptions import CertificateNotFoundError, InvalidCertificateError
from app.services.experts.usecases.manage_certificates import (
    AddCertificateUseCase,
    DeleteCertificateUseCase,
    UpdateCertificateUseCase,
)


class FakeCertificateRepository:
    def __init__(self) -> None:
        self.items: list[ExpertCertificate] = []
        self.next_id = 1

    async def list_certificates(self, user_id: int) -> list[ExpertCertificate]:
        return [item for item in self.items if item.user_id == user_id]

    async def get_certificate(self, user_id: int, certificate_id: int) -> ExpertCertificate | None:
        for item in self.items:
            if item.id == certificate_id and item.user_id == user_id:
                return item
        return None

    async def add_certificate(self, certificate: ExpertCertificate) -> ExpertCertificate:
        certificate.id = self.next_id
        self.next_id = self.next_id + 1
        self.items.append(certificate)
        return certificate

    async def remove_certificate(self, certificate: ExpertCertificate) -> None:
        self.items.remove(certificate)

    async def save(self) -> None:
        return None


def make_data(area: str = "Э1", object_code: str = "kl_tp", number: str = " 77-12345 ") -> CertificateInSchema:
    return CertificateInSchema(
        area_code=area,
        object_code=object_code,
        category=2,
        valid_until=date(2030, 1, 1),
        number=number,
    )


def test_expert_adds_certificate_with_clean_number() -> None:
    repo = FakeCertificateRepository()

    certificate = asyncio.run(AddCertificateUseCase(repo).execute(5, make_data()))

    assert certificate.user_id == 5
    assert certificate.number == "77-12345"
    assert len(repo.items) == 1


def test_add_rejects_duplicate_pair_and_empty_number() -> None:
    repo = FakeCertificateRepository()
    usecase = AddCertificateUseCase(repo)
    asyncio.run(usecase.execute(5, make_data()))

    with pytest.raises(InvalidCertificateError):
        asyncio.run(usecase.execute(5, make_data()))

    with pytest.raises(InvalidCertificateError):
        asyncio.run(usecase.execute(5, make_data("Э4", "kl", number="   ")))

    with pytest.raises(InvalidCertificateError):
        asyncio.run(usecase.execute(5, make_data("Э1", "d")))

    asyncio.run(usecase.execute(6, make_data()))
    assert len(repo.items) == 2


def test_update_keeps_own_pair_and_rejects_foreign() -> None:
    repo = FakeCertificateRepository()
    add = AddCertificateUseCase(repo)
    first = asyncio.run(add.execute(5, make_data()))
    second = asyncio.run(add.execute(5, make_data("Э4", "kl")))
    update = UpdateCertificateUseCase(repo)

    updated = asyncio.run(update.execute(5, first.id, make_data(number="99-1")))
    assert updated.number == "99-1"

    with pytest.raises(InvalidCertificateError):
        asyncio.run(update.execute(5, second.id, make_data()))

    with pytest.raises(CertificateNotFoundError):
        asyncio.run(update.execute(6, first.id, make_data()))


def test_last_certificate_cannot_be_deleted() -> None:
    repo = FakeCertificateRepository()
    add = AddCertificateUseCase(repo)
    first = asyncio.run(add.execute(5, make_data()))
    second = asyncio.run(add.execute(5, make_data("Э4", "kl")))
    delete = DeleteCertificateUseCase(repo)

    asyncio.run(delete.execute(5, second.id))
    assert [item.id for item in repo.items] == [first.id]

    with pytest.raises(InvalidCertificateError):
        asyncio.run(delete.execute(5, first.id))

    with pytest.raises(CertificateNotFoundError):
        asyncio.run(delete.execute(5, 999))
