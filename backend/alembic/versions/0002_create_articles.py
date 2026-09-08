"""create articles, tags, views and reactions

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-08
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    op.create_table(
        "articles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=400), nullable=True),
        sa.Column("cover_image", sa.String(length=500), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("toc", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("views_count", sa.Integer(), nullable=False),
        sa.Column("likes_count", sa.Integer(), nullable=False),
        sa.Column("dislikes_count", sa.Integer(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(
        op.f("ix_articles_published_at"), "articles", ["published_at"], unique=False
    )

    op.create_table(
        "article_tags",
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("article_id", "tag_id"),
    )

    op.create_table(
        "article_views",
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("visitor_id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("article_id", "visitor_id"),
    )

    op.create_table(
        "article_reactions",
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("visitor_id", sa.String(length=36), nullable=False),
        sa.Column("value", sa.SmallInteger(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("value IN (-1, 1)", name="ck_article_reactions_value"),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("article_id", "visitor_id"),
    )


def downgrade() -> None:
    op.drop_table("article_reactions")
    op.drop_table("article_views")
    op.drop_table("article_tags")
    op.drop_index(op.f("ix_articles_published_at"), table_name="articles")
    op.drop_table("articles")
    op.drop_table("tags")
