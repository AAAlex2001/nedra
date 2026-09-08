"""add seo fields to articles

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-08
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("articles", sa.Column("seo_title", sa.String(length=255), nullable=True))
    op.add_column(
        "articles", sa.Column("seo_description", sa.String(length=300), nullable=True)
    )
    op.add_column(
        "articles", sa.Column("seo_keywords", sa.String(length=500), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("articles", "seo_keywords")
    op.drop_column("articles", "seo_description")
    op.drop_column("articles", "seo_title")
