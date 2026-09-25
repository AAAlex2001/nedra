"""drop customer_companies: реквизиты заказчика теперь только в заявке

Revision ID: 0019
Revises: 0018
Create Date: 2026-09-25
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0019"
down_revision: Union[str, None] = "0018"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("customer_companies")


def downgrade() -> None:
    op.create_table(
        "customer_companies",
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("inn", sa.String(12), nullable=False),
        sa.Column("kpp", sa.String(9), nullable=True),
        sa.Column("address", sa.String(500), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
