"""expertise remarks: рекомендации эксперта и повторная подача документации

Revision ID: 0011
Revises: 0010
Create Date: 2026-09-20
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0011"
down_revision: Union[str, None] = "0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "expertise_remarks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("expertise_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["expertise_id"], ["expertises.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_expertise_remarks_expertise_id", "expertise_remarks", ["expertise_id"])

    op.add_column("expertise_documents", sa.Column("remark_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_expertise_documents_remark_id_expertise_remarks",
        "expertise_documents",
        "expertise_remarks",
        ["remark_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_expertise_documents_remark_id_expertise_remarks",
        "expertise_documents",
        type_="foreignkey",
    )
    op.drop_column("expertise_documents", "remark_id")
    op.drop_index("ix_expertise_remarks_expertise_id", table_name="expertise_remarks")
    op.drop_table("expertise_remarks")
