"""create expertises, expertise documents and notifications

Revision ID: 0009
Revises: 0008
Create Date: 2026-09-19
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0009"
down_revision: Union[str, None] = "0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "expertises",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("expert_id", sa.Integer(), nullable=True),
        sa.Column("object_code", sa.String(length=8), nullable=False),
        sa.Column("area_code", sa.String(length=8), nullable=False),
        sa.Column("hazard_class", sa.SmallInteger(), nullable=True),
        sa.Column("expert_category", sa.SmallInteger(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="new"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["customer_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["expert_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_expertises_customer_id", "expertises", ["customer_id"])
    op.create_index("ix_expertises_expert_id", "expertises", ["expert_id"])
    op.create_index("ix_expertises_object_code", "expertises", ["object_code"])
    op.create_index("ix_expertises_area_code", "expertises", ["area_code"])
    op.create_index("ix_expertises_status", "expertises", ["status"])

    op.create_table(
        "expertise_documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("expertise_id", sa.Integer(), nullable=False),
        sa.Column("uploaded_by", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False, server_default="documentation"),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("original_name", sa.String(length=255), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column("content_type", sa.String(length=128), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["expertise_id"], ["expertises.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="RESTRICT"),
    )
    op.create_index(
        "ix_expertise_documents_expertise_id", "expertise_documents", ["expertise_id"]
    )

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("expertise_id", sa.Integer(), nullable=True),
        sa.Column("text", sa.String(length=500), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["expertise_id"], ["expertises.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_table("notifications")
    op.drop_index("ix_expertise_documents_expertise_id", table_name="expertise_documents")
    op.drop_table("expertise_documents")
    op.drop_index("ix_expertises_status", table_name="expertises")
    op.drop_index("ix_expertises_area_code", table_name="expertises")
    op.drop_index("ix_expertises_object_code", table_name="expertises")
    op.drop_index("ix_expertises_expert_id", table_name="expertises")
    op.drop_index("ix_expertises_customer_id", table_name="expertises")
    op.drop_table("expertises")
