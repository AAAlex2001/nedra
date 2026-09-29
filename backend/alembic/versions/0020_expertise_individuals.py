"""expertise individuals: заказчик-физлицо и тип заказчика в заявке

Revision ID: 0020
Revises: 0019
Create Date: 2026-09-28
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0020"
down_revision: Union[str, None] = "0019"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "expertises",
        sa.Column("customer_type", sa.String(16), nullable=False, server_default="legal"),
    )

    op.create_table(
        "expertise_individuals",
        sa.Column(
            "expertise_id",
            sa.Integer(),
            sa.ForeignKey("expertises.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("passport_number", sa.String(20), nullable=False),
        sa.Column("passport_issued_by", sa.String(500), nullable=False),
        sa.Column("passport_issued_at", sa.Date(), nullable=False),
        sa.Column("address", sa.String(500), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("expertise_individuals")
    op.drop_column("expertises", "customer_type")
