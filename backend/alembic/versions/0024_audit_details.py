"""audit details: заявка на аудит СУПБ, торг по цене, План аудита и аудиторская группа

Revision ID: 0024
Revises: 0023
Create Date: 2026-10-08
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0024"
down_revision: Union[str, None] = "0023"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

JSON_TYPE = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def upgrade() -> None:
    op.add_column("expertises", sa.Column("audit_details", JSON_TYPE, nullable=True))
    op.add_column("expertises", sa.Column("offer_price", sa.Numeric(10, 2), nullable=True))
    op.add_column("expertises", sa.Column("counter_price", sa.Numeric(10, 2), nullable=True))
    op.add_column("expertises", sa.Column("audit_plan", JSON_TYPE, nullable=True))
    op.add_column("expertises", sa.Column("plan_comment", sa.Text(), nullable=True))
    op.add_column(
        "expertises", sa.Column("plan_sent_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "expertises", sa.Column("plan_approved_at", sa.DateTime(timezone=True), nullable=True)
    )

    op.add_column(
        "expert_profiles",
        sa.Column("audit_lead", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.create_table(
        "audit_team_members",
        sa.Column(
            "expertise_id",
            sa.Integer(),
            sa.ForeignKey("expertises.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )


def downgrade() -> None:
    op.drop_table("audit_team_members")
    op.drop_column("expert_profiles", "audit_lead")
    op.drop_column("expertises", "plan_approved_at")
    op.drop_column("expertises", "plan_sent_at")
    op.drop_column("expertises", "plan_comment")
    op.drop_column("expertises", "audit_plan")
    op.drop_column("expertises", "counter_price")
    op.drop_column("expertises", "offer_price")
    op.drop_column("expertises", "audit_details")
