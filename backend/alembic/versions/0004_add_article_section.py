"""add section to articles

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-08
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "articles",
        sa.Column("section", sa.String(length=16), nullable=False, server_default="blog"),
    )
    op.create_index("ix_articles_section", "articles", ["section"])


def downgrade() -> None:
    op.drop_index("ix_articles_section", table_name="articles")
    op.drop_column("articles", "section")
