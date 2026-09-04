"""create requests table

Revision ID: 0001
Revises:
Create Date: 2026-09-04
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("telephone", sa.String(length=32), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("activity", sa.Integer(), nullable=False),
        sa.Column("direction", sa.Integer(), nullable=False),
        sa.Column("company_name", sa.String(length=255), nullable=True),
        sa.Column("inn", sa.String(length=12), nullable=True),
        sa.Column("comment", sa.String(length=2000), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_requests_id"), "requests", ["id"], unique=False)
    op.create_index(
        op.f("ix_requests_direction"), "requests", ["direction"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_requests_direction"), table_name="requests")
    op.drop_index(op.f("ix_requests_id"), table_name="requests")
    op.drop_table("requests")
