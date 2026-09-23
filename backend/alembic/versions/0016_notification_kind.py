"""notification kind: тип уведомления, чтобы показывать важные всплывающим окном

Revision ID: 0016
Revises: 0015
Create Date: 2026-09-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0016"
down_revision: Union[str, None] = "0015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("notifications", sa.Column("kind", sa.String(32), nullable=True))


def downgrade() -> None:
    op.drop_column("notifications", "kind")
