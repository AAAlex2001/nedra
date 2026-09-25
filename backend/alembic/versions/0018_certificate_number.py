"""certificate number: номер удостоверения или регистрации в ЕРУЛ вместо скана

Revision ID: 0018
Revises: 0017
Create Date: 2026-09-25
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0018"
down_revision: Union[str, None] = "0017"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("expert_certificates", sa.Column("number", sa.String(64), nullable=True))


def downgrade() -> None:
    op.drop_column("expert_certificates", "number")
