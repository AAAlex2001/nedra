"""expertise optional fields: заказчик может не знать объект, область и категорию

Revision ID: 0015
Revises: 0014
Create Date: 2026-09-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0015"
down_revision: Union[str, None] = "0014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("expertises", sa.Column("deadline", sa.String(16), nullable=True))

    op.alter_column("expertises", "object_code", existing_type=sa.String(8), nullable=True)
    op.alter_column("expertises", "area_code", existing_type=sa.String(8), nullable=True)
    op.alter_column("expertises", "expert_category", existing_type=sa.SmallInteger(), nullable=True)


def downgrade() -> None:
    op.execute("UPDATE expertises SET object_code = 'kl' WHERE object_code IS NULL")
    op.execute("UPDATE expertises SET area_code = 'Э1' WHERE area_code IS NULL")
    op.execute("UPDATE expertises SET expert_category = 3 WHERE expert_category IS NULL")

    op.alter_column("expertises", "object_code", existing_type=sa.String(8), nullable=False)
    op.alter_column("expertises", "area_code", existing_type=sa.String(8), nullable=False)
    op.alter_column(
        "expertises", "expert_category", existing_type=sa.SmallInteger(), nullable=False
    )

    op.drop_column("expertises", "deadline")
