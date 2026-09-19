"""create expert applications, certificates and profiles

Revision ID: 0007
Revises: 0006
Create Date: 2026-09-19
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "expert_applications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=False),
        sa.Column("directions", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="pending"),
        sa.Column("admin_comment", sa.String(length=1000), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_expert_applications_email", "expert_applications", ["email"])
    op.create_index("ix_expert_applications_status", "expert_applications", ["status"])

    op.create_table(
        "expert_certificates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("application_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("area_code", sa.String(length=8), nullable=False),
        sa.Column("object_code", sa.String(length=8), nullable=False),
        sa.Column("category", sa.SmallInteger(), nullable=False),
        sa.Column("valid_until", sa.Date(), nullable=False),
        sa.Column("scan_path", sa.String(length=500), nullable=True),
        sa.Column("scan_name", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["application_id"], ["expert_applications.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_expert_certificates_application_id", "expert_certificates", ["application_id"]
    )
    op.create_index("ix_expert_certificates_user_id", "expert_certificates", ["user_id"])

    op.create_table(
        "expert_profiles",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("directions", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column(
            "approved_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("user_id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    op.drop_table("expert_profiles")
    op.drop_index("ix_expert_certificates_user_id", table_name="expert_certificates")
    op.drop_index("ix_expert_certificates_application_id", table_name="expert_certificates")
    op.drop_table("expert_certificates")
    op.drop_index("ix_expert_applications_status", table_name="expert_applications")
    op.drop_index("ix_expert_applications_email", table_name="expert_applications")
    op.drop_table("expert_applications")
