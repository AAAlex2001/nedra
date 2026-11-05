"""Запретить повторные заявки эксперта на рассмотрении."""

import sqlalchemy as sa

from alembic import op

revision = "0027"
down_revision = "0026"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Добавить уникальность активной заявки."""

    op.execute("LOCK TABLE expert_applications IN ACCESS EXCLUSIVE MODE")
    connection = op.get_bind()
    duplicate = connection.execute(
        sa.text(
            "SELECT email FROM expert_applications WHERE status = 'pending' "
            "GROUP BY email HAVING count(*) > 1 LIMIT 1"
        )
    ).first()
    if duplicate is not None:
        raise RuntimeError("Найдены повторные заявки эксперта на рассмотрении; сначала рассмотрите дубликаты")

    op.create_index(
        "uq_expert_applications_pending_email",
        "expert_applications",
        ["email"],
        unique=True,
        postgresql_where=sa.text("status = 'pending'"),
    )


def downgrade() -> None:
    """Снять ограничение повторных заявок."""

    op.drop_index("uq_expert_applications_pending_email", table_name="expert_applications")
