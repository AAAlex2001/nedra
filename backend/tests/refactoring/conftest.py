"""Изолированная база для нового приложения."""

import os
from collections.abc import AsyncIterator
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from src.audit.models.audit import Audit
from src.audit.site.schemas.create_audit import CreateAuditRequest
from src.core.models import Base
from src.core.settings import Settings
from src.users.enums import UserRole
from src.users.models.expert_profile import ExpertProfile
from src.users.models.user import User


@pytest.fixture
async def database_engine() -> AsyncIterator[AsyncEngine]:
    """Создать отдельную схему тестовой PostgreSQL."""

    database_url = os.environ.get("NEDRA_TEST_DATABASE_URL")
    if database_url is None:
        pytest.skip("Задайте NEDRA_TEST_DATABASE_URL с адресом отдельной тестовой PostgreSQL")

    schema_name = f"test_{uuid4().hex}"
    admin_engine = create_async_engine(database_url)
    async with admin_engine.begin() as connection:
        await connection.execute(text(f'CREATE SCHEMA "{schema_name}"'))

    engine = create_async_engine(
        database_url,
        connect_args={"server_settings": {"search_path": schema_name}},
    )

    try:
        yield engine
    finally:
        await engine.dispose()
        async with admin_engine.begin() as connection:
            await connection.execute(text(f'DROP SCHEMA "{schema_name}" CASCADE'))
        await admin_engine.dispose()


@pytest.fixture
async def session_factory(*, database_engine: AsyncEngine) -> AsyncIterator[async_sessionmaker]:
    """Открыть сессии для моделей нового приложения."""

    async with database_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield async_sessionmaker(database_engine, expire_on_commit=False)


@pytest.fixture
def settings() -> Settings:
    """Настройки без внешних сервисов."""

    return Settings(
        _env_file=None,
        database_url="sqlite+aiosqlite://",
        jwt_secret="test-secret-with-at-least-32-characters",
        smtp_host=None,
        smtp_user=None,
    )


@pytest.fixture
async def audit_ids(*, session_factory: async_sessionmaker) -> tuple[int, int, int]:
    """Создать заказчика, руководителя и новую заявку."""

    async with session_factory() as session:
        customer = User(
            email="customer@example.com",
            password_hash="unused",
            full_name="Заказчик",
            phone="+79990000001",
            role=UserRole.CUSTOMER,
        )
        lead = User(
            email="lead@example.com",
            password_hash="unused",
            full_name="Руководитель",
            phone="+79990000002",
            role=UserRole.EXPERT,
        )
        session.add_all([customer, lead])
        await session.flush()

        profile = ExpertProfile(user_id=lead.id, audit_lead=True, directions=["sms_audit"])
        session.add(profile)
        await session.flush()

        audit = Audit(customer_id=customer.id, negotiation_allowed=True)
        session.add(audit)
        await session.commit()

        return audit.id, customer.id, lead.id


@pytest.fixture
def audit_payload() -> CreateAuditRequest:
    """Заполненная анкета и реквизиты заказчика."""

    return CreateAuditRequest.model_validate(
        {
            "details": {
                "applicant": {
                    "full_name": "Иван Иванов",
                    "position": "Директор",
                    "organization": "ООО Испытание",
                    "inn": "1234567890",
                    "phone": "+79990000001",
                    "email": "customer@example.com",
                },
                "scope": "one",
                "objects": [
                    {
                        "reg_number": "А01-12345-0001",
                        "name": "Котельная",
                        "hazard_class": "III",
                        "address": "Москва, улица Испытаний, 1",
                        "industry": "Теплоснабжение",
                        "hazard_signs": ["pressure"],
                    },
                ],
                "stages": ["planning", "documents", "report"],
                "params": {"kind": "basic", "use_sto": False},
                "timing": {"kind": "month"},
                "budget": {"mode": "custom", "negotiation": "yes"},
            },
            "price": "150000.00",
            "company": {
                "full_name": "Общество с ограниченной ответственностью Испытание",
                "name": "ООО Испытание",
                "inn": "1234567890",
                "kpp": "123456789",
                "ogrn": "1234567890123",
                "address": "Москва, улица Испытаний, 1",
                "bank": "Тестовый банк",
                "bic": "123456789",
                "account": "12345678901234567890",
                "corr_account": "12345678901234567890",
                "signer_position": "Директор",
                "signer_name": "Иван Иванов",
                "signer_genitive": "директора Ивана Иванова",
            },
        }
    )
