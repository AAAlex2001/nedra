"""expertise flow: price, payments, step timestamps, result

Revision ID: 0010
Revises: 0009
Create Date: 2026-09-19
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0010"
down_revision: Union[str, None] = "0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("expertises", sa.Column("price", sa.Numeric(10, 2), nullable=True))
    op.add_column("expertises", sa.Column("result", sa.String(length=16), nullable=True))
    op.add_column("expertises", sa.Column("advance_payment_id", sa.Integer(), nullable=True))
    op.add_column("expertises", sa.Column("final_payment_id", sa.Integer(), nullable=True))
    op.add_column("expertises", sa.Column("expert_ready_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("expertises", sa.Column("contract_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("expertises", sa.Column("advance_paid_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("expertises", sa.Column("conclusion_ready_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("expertises", sa.Column("final_paid_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("expertises", sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("expertises", sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key(
        "fk_expertises_advance_payment_id_payments",
        "expertises",
        "payments",
        ["advance_payment_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_expertises_final_payment_id_payments",
        "expertises",
        "payments",
        ["final_payment_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_expertises_final_payment_id_payments", "expertises", type_="foreignkey")
    op.drop_constraint("fk_expertises_advance_payment_id_payments", "expertises", type_="foreignkey")
    op.drop_column("expertises", "accepted_at")
    op.drop_column("expertises", "sent_at")
    op.drop_column("expertises", "final_paid_at")
    op.drop_column("expertises", "conclusion_ready_at")
    op.drop_column("expertises", "advance_paid_at")
    op.drop_column("expertises", "contract_at")
    op.drop_column("expertises", "expert_ready_at")
    op.drop_column("expertises", "final_payment_id")
    op.drop_column("expertises", "advance_payment_id")
    op.drop_column("expertises", "result")
    op.drop_column("expertises", "price")
