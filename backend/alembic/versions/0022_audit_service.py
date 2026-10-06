"""audit service: заявки на аудит СУПБ рядом с экспертизами

Revision ID: 0022
Revises: 0021
Create Date: 2026-10-06
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0022"
down_revision: Union[str, None] = "0021"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "expertises",
        sa.Column("service", sa.String(16), nullable=False, server_default="expertise"),
    )
    op.create_index("ix_expertises_service", "expertises", ["service"])

    op.add_column("expertise_documents", sa.Column("item_number", sa.SmallInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column("expertise_documents", "item_number")
    op.drop_index("ix_expertises_service", table_name="expertises")
    op.drop_column("expertises", "service")
