"""Разделить заявки на экспертизы, аудиты и общие документы."""

from alembic import op

revision = "0026"
down_revision = "0025"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Перенести заявки в отдельные модели."""

    check_existing_requests()
    rename_common_request_table()
    create_expertise_table()
    create_audit_tables()
    move_customer_details()
    move_contracts_and_payments()
    move_remarks_and_documents()
    move_audit_team()
    remove_moved_request_columns()


def check_existing_requests() -> None:
    """Проверить данные перед разделением."""

    op.execute(
        """
        LOCK TABLE expertises, expertise_companies, expertise_individuals,
                   expertise_remarks, expertise_documents, audit_team_members,
                   invoices, notifications
        IN ACCESS EXCLUSIVE MODE
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM expertises
                WHERE service NOT IN ('expertise', 'audit')
                   OR customer_type NOT IN ('legal', 'entrepreneur', 'individual')
            ) THEN
                RAISE EXCEPTION 'Неизвестный вид услуги или заказчика: требуется проверка данных';
            END IF;

            IF EXISTS (
                SELECT 1
                FROM expertises AS request
                LEFT JOIN expertise_companies AS company ON company.expertise_id = request.id
                WHERE request.customer_type IN ('legal', 'entrepreneur') AND company.expertise_id IS NULL
            ) THEN
                RAISE EXCEPTION 'У заявки организации отсутствуют реквизиты: заполните их перед миграцией';
            END IF;

            IF EXISTS (
                SELECT 1
                FROM expertises AS request
                LEFT JOIN expertise_individuals AS person ON person.expertise_id = request.id
                WHERE request.customer_type = 'individual' AND person.expertise_id IS NULL
            ) THEN
                RAISE EXCEPTION 'У заявки физлица отсутствуют данные: заполните их перед миграцией';
            END IF;

            IF EXISTS (
                SELECT 1 FROM expertises
                WHERE service = 'audit'
                  AND (object_code IS NOT NULL OR area_code IS NOT NULL OR hazard_class IS NOT NULL
                       OR expert_category IS NOT NULL OR deadline IS NOT NULL)
            ) THEN
                RAISE EXCEPTION 'В аудите заполнены поля экспертизы: требуется проверка данных';
            END IF;

            IF EXISTS (
                SELECT 1 FROM expertises
                WHERE service = 'expertise'
                  AND (audit_details IS NOT NULL OR offer_price IS NOT NULL OR counter_price IS NOT NULL
                       OR audit_plan IS NOT NULL OR plan_comment IS NOT NULL
                       OR plan_sent_at IS NOT NULL OR plan_approved_at IS NOT NULL)
            ) THEN
                RAISE EXCEPTION 'В экспертизе заполнены поля аудита: требуется проверка данных';
            END IF;

            IF EXISTS (
                SELECT 1 FROM audit_team_members AS member
                JOIN expertises AS request ON request.id = member.expertise_id
                WHERE request.service <> 'audit'
            ) THEN
                RAISE EXCEPTION 'Аудиторская группа связана с экспертизой: требуется проверка данных';
            END IF;
        END $$
        """
    )


def rename_common_request_table() -> None:
    """Сохранить номера заявок и существующие внешние ключи."""

    op.rename_table("expertises", "service_requests")
    op.execute("ALTER TABLE service_requests RENAME CONSTRAINT expertises_pkey TO service_requests_pkey")
    op.execute("ALTER SEQUENCE expertises_id_seq RENAME TO service_requests_id_seq")
    op.alter_column("service_requests", "service", new_column_name="service_type", server_default=None)
    op.execute("ALTER INDEX ix_expertises_customer_id RENAME TO ix_service_requests_customer_id")
    op.execute("ALTER INDEX ix_expertises_service RENAME TO ix_service_requests_service_type")
    op.create_check_constraint(
        "ck_service_requests_service_type",
        "service_requests",
        "service_type IN ('expertise', 'audit')",
    )


def create_expertise_table() -> None:
    """Перенести этапы и условия экспертиз."""

    op.execute(
        """
        CREATE TABLE expertises (
            request_id integer PRIMARY KEY REFERENCES service_requests(id) ON DELETE CASCADE,
            expert_id integer REFERENCES users(id) ON DELETE SET NULL,
            status varchar(32) NOT NULL,
            object_name varchar(500),
            object_code varchar(8),
            area_code varchar(8),
            hazard_class smallint,
            expert_category smallint,
            deadline varchar(16),
            price numeric(10, 2),
            result varchar(16),
            expert_ready_at timestamptz,
            conclusion_ready_at timestamptz,
            sent_at timestamptz,
            accepted_at timestamptz
        )
        """
    )
    op.execute(
        """
        INSERT INTO expertises (
            request_id, expert_id, status, object_name, object_code, area_code,
            hazard_class, expert_category, deadline, price, result,
            expert_ready_at, conclusion_ready_at, sent_at, accepted_at
        )
        SELECT id, expert_id, status, object_name, object_code, area_code,
               hazard_class, expert_category, deadline, price, result,
               expert_ready_at, conclusion_ready_at, sent_at, accepted_at
        FROM service_requests
        WHERE service_type = 'expertise'
        """
    )


def create_audit_tables() -> None:
    """Перенести аудит, анкету и план."""

    op.execute(
        """
        CREATE TABLE audits (
            request_id integer PRIMARY KEY REFERENCES service_requests(id) ON DELETE CASCADE,
            lead_id integer REFERENCES users(id) ON DELETE SET NULL,
            status varchar(32) NOT NULL,
            customer_budget numeric(10, 2),
            negotiation_allowed boolean NOT NULL,
            offer_price numeric(10, 2),
            counter_price numeric(10, 2),
            agreed_price numeric(10, 2),
            result varchar(16),
            lead_ready_at timestamptz,
            conclusion_ready_at timestamptz,
            sent_at timestamptz,
            accepted_at timestamptz
        )
        """
    )
    op.create_index("ix_audits_lead_id", "audits", ["lead_id"])
    op.create_index("ix_audits_status", "audits", ["status"])
    op.execute(
        """
        INSERT INTO audits (
            request_id, lead_id, status, customer_budget, negotiation_allowed,
            offer_price, counter_price, agreed_price, result, lead_ready_at,
            conclusion_ready_at, sent_at, accepted_at
        )
        SELECT id, expert_id, status,
               CASE WHEN status IN ('new', 'consultation', 'offer', 'counter') THEN price END,
               COALESCE(audit_details -> 'budget' ->> 'negotiation', 'yes') <> 'no',
               offer_price, counter_price,
               CASE WHEN status NOT IN ('new', 'consultation', 'offer', 'counter') THEN price END,
               result, expert_ready_at, conclusion_ready_at, sent_at, accepted_at
        FROM service_requests
        WHERE service_type = 'audit'
        """
    )
    op.execute(
        """
        CREATE TABLE audit_applications (
            request_id integer PRIMARY KEY REFERENCES audits(request_id) ON DELETE CASCADE,
            object_name varchar(500),
            details jsonb
        )
        """
    )
    op.execute(
        """
        INSERT INTO audit_applications (request_id, object_name, details)
        SELECT id, object_name, audit_details FROM service_requests WHERE service_type = 'audit'
        """
    )
    op.execute(
        """
        CREATE TABLE audit_plans (
            request_id integer PRIMARY KEY REFERENCES audits(request_id) ON DELETE CASCADE,
            plan jsonb,
            comment text,
            sent_at timestamptz,
            approved_at timestamptz
        )
        """
    )
    op.execute(
        """
        INSERT INTO audit_plans (request_id, plan, comment, sent_at, approved_at)
        SELECT id, audit_plan, plan_comment, plan_sent_at, plan_approved_at
        FROM service_requests WHERE service_type = 'audit'
        """
    )


def move_customer_details() -> None:
    """Привязать реквизиты и паспортные данные к общей заявке."""

    op.rename_table("expertise_companies", "request_companies")
    op.alter_column("request_companies", "expertise_id", new_column_name="request_id")
    op.execute("ALTER TABLE request_companies ADD COLUMN customer_type varchar(16)")
    op.execute(
        """
        UPDATE request_companies AS company
        SET customer_type = request.customer_type
        FROM service_requests AS request WHERE request.id = company.request_id
        """
    )
    op.alter_column("request_companies", "customer_type", nullable=False)
    op.rename_table("expertise_individuals", "request_individuals")
    op.alter_column("request_individuals", "expertise_id", new_column_name="request_id")


def move_contracts_and_payments() -> None:
    """Перенести договоры и этапы оплаты."""

    op.execute(
        """
        CREATE TABLE contracts (
            request_id integer PRIMARY KEY REFERENCES service_requests(id) ON DELETE CASCADE,
            kind varchar(16),
            confirmed_at timestamptz
        )
        """
    )
    op.execute(
        """
        INSERT INTO contracts (request_id, kind, confirmed_at)
        SELECT id, contract_kind, contract_at FROM service_requests
        """
    )
    op.execute(
        """
        CREATE TABLE request_payments (
            request_id integer REFERENCES service_requests(id) ON DELETE CASCADE,
            stage varchar(16),
            payment_id integer REFERENCES payments(id) ON DELETE SET NULL,
            paid_at timestamptz,
            PRIMARY KEY (request_id, stage),
            CONSTRAINT ck_request_payments_stage CHECK (stage IN ('advance', 'final'))
        )
        """
    )
    op.create_index("ix_request_payments_payment_id", "request_payments", ["payment_id"])
    op.execute(
        """
        INSERT INTO request_payments (request_id, stage, payment_id, paid_at)
        SELECT id, 'advance', advance_payment_id, advance_paid_at
        FROM service_requests WHERE advance_payment_id IS NOT NULL OR advance_paid_at IS NOT NULL
        UNION ALL
        SELECT id, 'final', final_payment_id, final_paid_at
        FROM service_requests WHERE final_payment_id IS NOT NULL OR final_paid_at IS NOT NULL
        """
    )
    op.alter_column("invoices", "expertise_id", new_column_name="request_id")
    op.execute("ALTER INDEX ix_invoices_expertise_id RENAME TO ix_invoices_request_id")
    op.alter_column("notifications", "expertise_id", new_column_name="request_id")
    op.create_index("ix_notifications_request_id", "notifications", ["request_id"])


def move_remarks_and_documents() -> None:
    """Разделить замечания и сохранить ссылки документов."""

    op.execute(
        """
        CREATE TABLE audit_remarks (
            id serial PRIMARY KEY,
            request_id integer NOT NULL REFERENCES audits(request_id) ON DELETE CASCADE,
            text text,
            response_text text,
            created_at timestamptz NOT NULL DEFAULT now(),
            resolved_at timestamptz
        )
        """
    )
    op.create_index("ix_audit_remarks_request_id", "audit_remarks", ["request_id"])
    op.execute(
        """
        INSERT INTO audit_remarks (id, request_id, text, response_text, created_at, resolved_at)
        SELECT remark.id, remark.expertise_id, remark.text,
               remark.response_text, remark.created_at, remark.resolved_at
        FROM expertise_remarks AS remark
        JOIN audits AS audit ON audit.request_id = remark.expertise_id
        """
    )
    op.execute(
        """
        SELECT setval(
            pg_get_serial_sequence('audit_remarks', 'id'),
            COALESCE((SELECT max(id) FROM audit_remarks), 1),
            EXISTS (SELECT 1 FROM audit_remarks)
        )
        """
    )

    op.rename_table("expertise_documents", "request_documents")
    op.execute("ALTER SEQUENCE expertise_documents_id_seq RENAME TO request_documents_id_seq")
    op.alter_column("request_documents", "expertise_id", new_column_name="request_id")
    op.alter_column("request_documents", "remark_id", new_column_name="expertise_remark_id")
    op.execute("ALTER TABLE request_documents ADD COLUMN audit_remark_id integer")
    op.create_foreign_key(
        "fk_request_documents_audit_remark",
        "request_documents",
        "audit_remarks",
        ["audit_remark_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.execute(
        """
        UPDATE request_documents
        SET audit_remark_id = expertise_remark_id, expertise_remark_id = NULL
        WHERE expertise_remark_id IN (SELECT id FROM audit_remarks)
        """
    )
    op.create_check_constraint(
        "ck_request_documents_single_remark",
        "request_documents",
        "expertise_remark_id IS NULL OR audit_remark_id IS NULL",
    )
    op.execute("ALTER INDEX ix_expertise_documents_expertise_id RENAME TO ix_request_documents_request_id")
    op.create_index("ix_request_documents_expertise_remark_id", "request_documents", ["expertise_remark_id"])
    op.create_index("ix_request_documents_audit_remark_id", "request_documents", ["audit_remark_id"])

    op.execute("DELETE FROM expertise_remarks WHERE id IN (SELECT id FROM audit_remarks)")
    op.alter_column("expertise_remarks", "expertise_id", new_column_name="request_id")
    op.drop_constraint("expertise_remarks_expertise_id_fkey", "expertise_remarks", type_="foreignkey")
    op.create_foreign_key(
        "fk_expertise_remarks_request",
        "expertise_remarks",
        "expertises",
        ["request_id"],
        ["request_id"],
        ondelete="CASCADE",
    )
    op.execute("ALTER INDEX ix_expertise_remarks_expertise_id RENAME TO ix_expertise_remarks_request_id")


def move_audit_team() -> None:
    """Привязать участников группы к аудитам."""

    op.alter_column("audit_team_members", "expertise_id", new_column_name="request_id")
    op.drop_constraint("audit_team_members_expertise_id_fkey", "audit_team_members", type_="foreignkey")
    op.create_foreign_key(
        "fk_audit_team_members_request",
        "audit_team_members",
        "audits",
        ["request_id"],
        ["request_id"],
        ondelete="CASCADE",
    )
    op.drop_constraint("audit_team_members_user_id_fkey", "audit_team_members", type_="foreignkey")
    op.create_foreign_key(
        "fk_audit_team_members_user",
        "audit_team_members",
        "users",
        ["user_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_audit_team_members_user_id", "audit_team_members", ["user_id"])


def remove_moved_request_columns() -> None:
    """Оставить в общей заявке только общие сведения."""

    op.execute(
        """
        ALTER TABLE service_requests
            DROP COLUMN expert_id,
            DROP COLUMN object_code,
            DROP COLUMN area_code,
            DROP COLUMN hazard_class,
            DROP COLUMN expert_category,
            DROP COLUMN deadline,
            DROP COLUMN object_name,
            DROP COLUMN contract_kind,
            DROP COLUMN customer_type,
            DROP COLUMN audit_details,
            DROP COLUMN status,
            DROP COLUMN price,
            DROP COLUMN offer_price,
            DROP COLUMN counter_price,
            DROP COLUMN audit_plan,
            DROP COLUMN plan_comment,
            DROP COLUMN result,
            DROP COLUMN advance_payment_id,
            DROP COLUMN final_payment_id,
            DROP COLUMN expert_ready_at,
            DROP COLUMN contract_at,
            DROP COLUMN advance_paid_at,
            DROP COLUMN plan_sent_at,
            DROP COLUMN plan_approved_at,
            DROP COLUMN conclusion_ready_at,
            DROP COLUMN final_paid_at,
            DROP COLUMN sent_at,
            DROP COLUMN accepted_at
        """
    )
    op.create_index("ix_expertises_expert_id", "expertises", ["expert_id"])
    op.create_index("ix_expertises_object_code", "expertises", ["object_code"])
    op.create_index("ix_expertises_area_code", "expertises", ["area_code"])
    op.create_index("ix_expertises_status", "expertises", ["status"])


def downgrade() -> None:
    """Запретить откат с потерей новых данных."""

    raise RuntimeError(
        "После разделения исходный бюджет и согласованная цена хранятся отдельно, "
        "а номера замечаний экспертизы и аудита могут совпадать. "
        "Старая схема не сохраняет эти данные без потерь. "
        "Для возврата к версии 0025 восстановите резервную копию до миграции."
    )
