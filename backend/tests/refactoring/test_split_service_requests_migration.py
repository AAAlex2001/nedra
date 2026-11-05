"""Перенос существующих заявок в новую схему."""

import importlib.util
import os
from pathlib import Path

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncEngine

from alembic.migration import MigrationContext
from alembic.operations import Operations
from src.core.models import Base

pytestmark = pytest.mark.skipif(
    not os.environ.get("NEDRA_TEST_DATABASE_URL"),
    reason="Для миграции нужна PostgreSQL",
)


def apply_revision(*, connection: Connection, path: Path) -> None:
    """Выполнить миграцию в изолированной схеме."""

    specification = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    context = MigrationContext.configure(connection)

    with Operations.context(context):
        module.upgrade()


def create_legacy_schema(connection: Connection) -> None:
    """Пройти существующие миграции до версии 0025."""

    versions = Path(__file__).resolve().parents[2] / "alembic" / "versions"
    for path in sorted(versions.glob("*.py")):
        if path.name[:4] <= "0025":
            apply_revision(connection=connection, path=path)


def split_service_requests(connection: Connection) -> None:
    """Выполнить разделение заявок."""

    path = (
        Path(__file__).resolve().parents[2]
        / "alembic"
        / "versions"
        / "0026_split_service_requests.py"
    )
    apply_revision(connection=connection, path=path)


def insert_legacy_requests(connection: Connection) -> None:
    """Заполнить старую схему связанными данными."""

    connection.execute(
        text(
            """
            INSERT INTO users (id, email, password_hash, full_name, phone, role)
            VALUES (1, 'customer@example.com', 'unused', 'Заказчик', '+79990000001', 'customer'),
                   (2, 'expert@example.com', 'unused', 'Эксперт', '+79990000002', 'expert')
            """
        )
    )
    connection.execute(
        text(
            """
            INSERT INTO payments (
                id, user_id, amount, currency, description, status, provider_payment_id, paid_at
            )
            VALUES (70, 1, 20000, 'RUB', 'Аванс', 'succeeded', 'provider-70', '2026-10-01T10:00:00Z')
            """
        )
    )
    connection.execute(
        text(
            """
            INSERT INTO expertises (
                id, customer_id, expert_id, service, customer_type, object_name, object_code,
                area_code, expert_category, comment, status, price, result, contract_kind,
                advance_payment_id, advance_paid_at, final_paid_at,
                expert_ready_at, contract_at, conclusion_ready_at, sent_at, accepted_at
            )
            VALUES (
                10, 1, 2, 'expertise', 'individual', 'Документация', 'tp', 'Э1', 1,
                'Комментарий к экспертизе', 'accepted', 40000, 'positive', 'reequipment',
                70, '2026-10-01T10:00:00Z', '2026-10-02T10:00:00Z',
                '2026-09-30T10:00:00Z', '2026-09-30T11:00:00Z',
                '2026-10-02T09:00:00Z', '2026-10-02T11:00:00Z', '2026-10-03T10:00:00Z'
            )
            """
        )
    )
    connection.execute(
        text(
            """
            INSERT INTO expertises (
                id, customer_id, expert_id, service, customer_type, object_name,
                status, price, offer_price, counter_price, audit_details,
                audit_plan, plan_comment, plan_sent_at, plan_approved_at, contract_kind, result
            )
            VALUES (
                20, 1, 2, 'audit', 'entrepreneur', 'Сохранённое название аудита',
                'counter', 100000, 150000, 130000,
                '{"budget": {"mode": "custom", "negotiation": "yes"}}',
                '{"version": 2}', 'Комментарий к плану', '2026-10-01T10:00:00Z',
                '2026-10-02T10:00:00Z', 'audit', 'negative'
            )
            """
        )
    )
    connection.execute(
        text(
            """
            INSERT INTO expertise_companies (
                expertise_id, full_name, name, inn, ogrn, address, bank, bic,
                account, corr_account, signer_position, signer_name, signer_genitive, signer_basis
            )
            VALUES (
                20, 'Индивидуальный предприниматель Иванов', 'ИП Иванов', '123456789012',
                '123456789012345', 'Москва, улица 1', 'Банк', '123456789',
                '12345678901234567890', '12345678901234567890',
                'Предприниматель', 'Иванов Иван', 'Иванова Ивана', 'Регистрации'
            )
            """
        )
    )
    connection.execute(
        text(
            """
            INSERT INTO expertise_individuals (
                expertise_id, full_name, passport_number, passport_issued_by, passport_issued_at, address
            )
            VALUES (10, 'Заказчик', '4510 123456', 'Тестовый отдел', '2020-01-01', 'Москва, улица 2')
            """
        )
    )
    connection.execute(
        text(
            """
            INSERT INTO expertise_remarks (id, expertise_id, text, response_text, resolved_at)
            VALUES (101, 10, 'Замечание эксперта', 'Ответ эксперту', '2026-10-01T12:00:00Z'),
                   (102, 20, 'Замечание аудитора', 'Ответ аудитору', '2026-10-02T12:00:00Z')
            """
        )
    )
    connection.execute(
        text(
            """
            INSERT INTO expertise_documents (
                id, expertise_id, remark_id, uploaded_by, kind, file_path,
                original_name, size, content_type, item_number
            )
            VALUES (201, 10, 101, 2, 'remark', 'documents/expertise.pdf', 'Экспертиза.pdf', 100,
                    'application/pdf', NULL),
                   (202, 20, 102, 2, 'remark', 'documents/audit.pdf', 'Аудит.pdf', 200,
                    'application/pdf', 3)
            """
        )
    )
    connection.execute(
        text(
            """
            INSERT INTO invoices (id, expertise_id, stage, amount, payer_name, payer_inn, payer_address)
            VALUES (90, 20, 'advance', 50000, 'ИП Иванов', '123456789012', 'Старый адрес плательщика')
            """
        )
    )
    connection.execute(
        text(
            "INSERT INTO notifications (id, user_id, expertise_id, text) VALUES (300, 1, 20, 'Уведомление')"
        )
    )
    connection.execute(
        text("INSERT INTO audit_team_members (expertise_id, user_id) VALUES (20, 2)")
    )
    connection.execute(text("SELECT setval(pg_get_serial_sequence('expertises', 'id'), 20)"))
    connection.execute(
        text("SELECT setval(pg_get_serial_sequence('expertise_remarks', 'id'), 102)")
    )
    connection.execute(
        text("SELECT setval(pg_get_serial_sequence('expertise_documents', 'id'), 202)")
    )


@pytest.fixture
async def legacy_engine(*, database_engine: AsyncEngine) -> AsyncEngine:
    """Подготовить схему версии 0025 с заявками."""

    async with database_engine.begin() as connection:
        await connection.run_sync(create_legacy_schema)
        await connection.run_sync(insert_legacy_requests)

    return database_engine


async def test_migration_preserves_requests_and_references(*, legacy_engine: AsyncEngine) -> None:
    """Сохранить номера, поля и связи существующих заявок."""

    async with legacy_engine.begin() as connection:
        await connection.run_sync(split_service_requests)

    async with legacy_engine.connect() as connection:
        requests = await connection.execute(
            text("SELECT id, service_type FROM service_requests ORDER BY id")
        )
        assert requests.all() == [(10, "expertise"), (20, "audit")]

        expertise = await connection.execute(text("SELECT * FROM expertises WHERE request_id = 10"))
        expertise_data = expertise.mappings().one()
        assert expertise_data["status"] == "accepted"
        assert expertise_data["price"] == 40000
        assert expertise_data["result"] == "positive"
        assert expertise_data["object_code"] == "tp"
        assert expertise_data["accepted_at"].isoformat() == "2026-10-03T10:00:00+00:00"

        audit = await connection.execute(text("SELECT * FROM audits WHERE request_id = 20"))
        audit_data = audit.mappings().one()
        assert audit_data["customer_budget"] == 100000
        assert audit_data["offer_price"] == 150000
        assert audit_data["counter_price"] == 130000
        assert audit_data["agreed_price"] is None
        assert audit_data["result"] == "negative"

        application = await connection.execute(
            text("SELECT * FROM audit_applications WHERE request_id = 20")
        )
        application_data = application.mappings().one()
        assert application_data["object_name"] == "Сохранённое название аудита"
        assert application_data["details"]["budget"]["mode"] == "custom"

        plan = await connection.execute(text("SELECT * FROM audit_plans WHERE request_id = 20"))
        plan_data = plan.mappings().one()
        assert plan_data["plan"] == {"version": 2}
        assert plan_data["comment"] == "Комментарий к плану"
        assert plan_data["approved_at"].isoformat() == "2026-10-02T10:00:00+00:00"

        documents = await connection.execute(
            text(
                "SELECT id, request_id, expertise_remark_id, audit_remark_id, file_path, item_number "
                "FROM request_documents ORDER BY id"
            )
        )
        assert documents.all() == [
            (201, 10, 101, None, "documents/expertise.pdf", None),
            (202, 20, None, 102, "documents/audit.pdf", 3),
        ]
        assert await connection.scalar(
            text("SELECT response_text FROM audit_remarks WHERE id = 102")
        ) == ("Ответ аудитору")
        assert await connection.scalar(text("SELECT count(*) FROM expertise_remarks")) == 1
        assert (
            await connection.scalar(text("SELECT request_id FROM notifications WHERE id = 300"))
            == 20
        )
        assert await connection.scalar(text("SELECT request_id FROM invoices WHERE id = 90")) == 20
        assert await connection.scalar(
            text("SELECT payer_address FROM invoices WHERE id = 90")
        ) == ("Старый адрес плательщика")
        assert await connection.scalar(text("SELECT request_id FROM audit_team_members")) == 20
        assert (
            await connection.scalar(text("SELECT customer_type FROM request_companies"))
            == "entrepreneur"
        )
        assert (
            await connection.scalar(text("SELECT passport_number FROM request_individuals"))
            == "4510 123456"
        )
        assert (
            await connection.scalar(text("SELECT kind FROM contracts WHERE request_id = 20"))
            == "audit"
        )

        payments = await connection.execute(
            text(
                "SELECT stage, payment_id, paid_at IS NOT NULL FROM request_payments ORDER BY stage"
            )
        )
        assert payments.all() == [("advance", 70, True), ("final", None, True)]


async def test_migrated_columns_match_models(*, legacy_engine: AsyncEngine) -> None:
    """Сверить состав таблиц с новыми моделями."""

    def compare_columns(connection: Connection) -> None:
        """Сравнить имена и обязательность колонок."""

        inspector = inspect(connection)
        for table in Base.metadata.sorted_tables:
            columns = inspector.get_columns(table.name)
            actual_columns = {column["name"]: column["nullable"] for column in columns}
            expected_columns = {column.name: column.nullable for column in table.columns}
            assert actual_columns == expected_columns, table.name
            actual_types = {
                column["name"]: column["type"].compile(dialect=connection.dialect)
                for column in columns
            }
            expected_types = {
                column.name: column.type.compile(dialect=connection.dialect)
                for column in table.columns
            }
            assert actual_types == expected_types, table.name

    async with legacy_engine.begin() as connection:
        await connection.run_sync(split_service_requests)
        await connection.run_sync(restrict_pending_applications)
        await connection.run_sync(separate_services)
        await connection.run_sync(
            lambda connection: apply_revision(
                connection=connection,
                path=Path(__file__).resolve().parents[2]
                / "alembic/versions/0029_article_content.py",
            )
        )
        await connection.run_sync(compare_columns)


async def test_article_content_migration_preserves_publications(
    *,
    legacy_engine: AsyncEngine,
) -> None:
    """Сохранить текст, адрес, теги и счётчики."""

    async with legacy_engine.begin() as connection:
        await connection.execute(
            text("""
            INSERT INTO articles (
                id, slug, title, section, content, toc, documents,
                seo_title, seo_description, seo_keywords,
                views_count, likes_count, dislikes_count
            ) VALUES (
                42, 'saved-article', 'Сохранённая статья', 'news', '<h2>Текст</h2>',
                '[{"id":"text","title":"Текст"}]', '[]',
                'SEO', 'Описание', 'слова', 17, 5, 2
            )
        """)
        )
        await connection.execute(
            text("""
            INSERT INTO tags (id, slug, title) VALUES (42, 'saved-tag', 'Тег');
        """)
        )
        await connection.execute(
            text("""
            INSERT INTO article_tags (article_id, tag_id) VALUES (42, 42)
        """)
        )
        await connection.run_sync(
            lambda connection: apply_revision(
                connection=connection,
                path=Path(__file__).resolve().parents[2]
                / "alembic/versions/0029_article_content.py",
            )
        )
        article = (
            await connection.execute(
                text(
                    "SELECT slug, views_count, likes_count, dislikes_count FROM articles WHERE id = 42"
                )
            )
        ).one()
        assert tuple(article) == ("saved-article", 17, 5, 2)
        content = (
            await connection.execute(
                text(
                    "SELECT content, toc, seo_title, seo_description, seo_keywords "
                    "FROM article_contents WHERE article_id = 42"
                )
            )
        ).one()
        assert tuple(content) == (
            "<h2>Текст</h2>",
            [{"id": "text", "title": "Текст"}],
            "SEO",
            "Описание",
            "слова",
        )
        assert (
            await connection.scalar(text("SELECT tag_id FROM article_tags WHERE article_id = 42"))
            == 42
        )


async def test_sequences_continue_after_migration(*, legacy_engine: AsyncEngine) -> None:
    """Выдать новые номера без пересечения с перенесёнными."""

    async with legacy_engine.begin() as connection:
        await connection.run_sync(split_service_requests)
        request_id = await connection.scalar(
            text(
                "INSERT INTO service_requests (customer_id, service_type) VALUES (1, 'audit') RETURNING id"
            )
        )
        remark_id = await connection.scalar(
            text(
                "INSERT INTO audit_remarks (request_id, text) VALUES (20, 'Новое замечание') RETURNING id"
            )
        )

        assert request_id == 21
        assert remark_id == 103


async def test_incomplete_customer_data_stops_migration(*, legacy_engine: AsyncEngine) -> None:
    """Остановить перенос вместо потери вида заказчика."""

    async with legacy_engine.begin() as connection:
        await connection.execute(text("DELETE FROM expertise_companies WHERE expertise_id = 20"))

    with pytest.raises(DBAPIError, match="отсутствуют реквизиты"):
        async with legacy_engine.begin() as connection:
            await connection.run_sync(split_service_requests)

    async with legacy_engine.connect() as connection:
        assert await connection.scalar(text("SELECT count(*) FROM expertises")) == 2
        assert await connection.scalar(text("SELECT count(*) FROM expertise_documents")) == 2
        assert await connection.scalar(text("SELECT to_regclass('service_requests')")) is None


def restrict_pending_applications(connection: Connection) -> None:
    """Запретить повторные активные заявки эксперта."""

    path = (
        Path(__file__).resolve().parents[2]
        / "alembic"
        / "versions"
        / "0027_unique_pending_expert_application.py"
    )
    apply_revision(connection=connection, path=path)


async def test_pending_application_migration_keeps_reviewed_history(
    *, legacy_engine: AsyncEngine
) -> None:
    """Разрешить повторную подачу после отказа и запретить два ожидания."""

    statement = text(
        "INSERT INTO expert_applications (email, password_hash, full_name, phone, directions, status) "
        "VALUES ('expert@example.com', 'unused', 'Эксперт', '+79990000001', '[]', :status)"
    )
    async with legacy_engine.begin() as connection:
        await connection.run_sync(split_service_requests)
        await connection.run_sync(restrict_pending_applications)
        await connection.execute(statement, {"status": "rejected"})
        await connection.execute(statement, {"status": "pending"})

    with pytest.raises(DBAPIError):
        async with legacy_engine.begin() as connection:
            await connection.execute(statement, {"status": "pending"})

    async with legacy_engine.connect() as connection:
        assert await connection.scalar(text("SELECT count(*) FROM expert_applications")) == 2


async def test_pending_application_migration_preserves_duplicates_for_review(
    *, legacy_engine: AsyncEngine
) -> None:
    """Остановить миграцию без удаления повторных заявок."""

    async with legacy_engine.begin() as connection:
        await connection.run_sync(split_service_requests)
        await connection.execute(
            text(
                "INSERT INTO expert_applications (email, password_hash, full_name, phone, directions, status) "
                "VALUES ('expert@example.com', 'first', 'Первый', '+79990000001', '[]', 'pending'), "
                "('expert@example.com', 'second', 'Второй', '+79990000002', '[]', 'pending')"
            )
        )

    with pytest.raises(RuntimeError, match="повторные заявки"):
        async with legacy_engine.begin() as connection:
            await connection.run_sync(restrict_pending_applications)

    async with legacy_engine.connect() as connection:
        assert await connection.scalar(text("SELECT count(*) FROM expert_applications")) == 2


def separate_services(connection: Connection) -> None:
    """Удалить общую заявку и разделить связи услуг."""

    path = (
        Path(__file__).resolve().parents[2]
        / "alembic"
        / "versions"
        / "0028_independent_audits_and_expertises.py"
    )
    apply_revision(connection=connection, path=path)


async def test_independent_services_keep_documents_and_payments(
    *, legacy_engine: AsyncEngine
) -> None:
    """Сохранить историю и создать независимые номера услуг."""

    async with legacy_engine.begin() as connection:
        await connection.run_sync(split_service_requests)
        await connection.run_sync(restrict_pending_applications)
        await connection.run_sync(separate_services)

        assert await connection.scalar(text("SELECT to_regclass('service_requests')")) is None
        assert await connection.scalar(text("SELECT customer_id FROM audits WHERE id = 20")) == 1
        assert (
            await connection.scalar(text("SELECT customer_type FROM audits WHERE id = 20"))
            == "entrepreneur"
        )
        assert (
            await connection.scalar(text("SELECT customer_type FROM expertises WHERE id = 10"))
            == "individual"
        )
        assert (
            await connection.scalar(
                text("SELECT passport_number FROM expertise_individuals WHERE expertise_id = 10")
            )
            == "4510 123456"
        )
        assert (
            await connection.scalar(text("SELECT file_path FROM audit_documents WHERE id = 202"))
            == "documents/audit.pdf"
        )
        assert (
            await connection.scalar(text("SELECT remark_id FROM audit_documents WHERE id = 202"))
            == 102
        )
        assert (
            await connection.scalar(
                text("SELECT file_path FROM expertise_documents WHERE id = 201")
            )
            == "documents/expertise.pdf"
        )
        assert (
            await connection.scalar(text("SELECT audit_id FROM notifications WHERE id = 300")) == 20
        )
        assert (
            await connection.scalar(text("SELECT expertise_id FROM notifications WHERE id = 300"))
            is None
        )
        assert await connection.scalar(text("SELECT audit_id FROM invoices WHERE id = 90")) == 20
        assert (
            await connection.scalar(
                text(
                    "SELECT payment_id FROM expertise_payments WHERE expertise_id = 10 AND stage = 'advance'"
                )
            )
            == 70
        )
        assert (
            await connection.scalar(text("SELECT kind FROM contracts WHERE audit_id = 20"))
            == "audit"
        )
        assert (
            await connection.scalar(text("SELECT kind FROM contracts WHERE expertise_id = 10"))
            == "reequipment"
        )
        new_audit = await connection.scalar(
            text(
                "INSERT INTO audits (customer_id, customer_type, status, negotiation_allowed) VALUES (1, 'legal', 'new', true) RETURNING id"
            )
        )
        new_expertise = await connection.scalar(
            text(
                "INSERT INTO expertises (customer_id, customer_type, status) VALUES (1, 'legal', 'new') RETURNING id"
            )
        )
        assert new_audit == 21
        assert new_expertise == 11
