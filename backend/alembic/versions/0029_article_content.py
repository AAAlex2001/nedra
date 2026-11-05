"""Отделить содержимое статей от карточек."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0029"
down_revision = "0028"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Перенести тексты без изменения адресов и счётчиков."""

    op.execute("LOCK TABLE articles IN ACCESS EXCLUSIVE MODE")
    op.create_table(
        "article_contents",
        sa.Column("article_id", sa.Integer(), sa.ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("toc", postgresql.JSONB(), nullable=False),
        sa.Column("documents", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("seo_title", sa.String(255), nullable=True),
        sa.Column("seo_description", sa.String(300), nullable=True),
        sa.Column("seo_keywords", sa.String(500), nullable=True),
    )
    op.execute("""
        INSERT INTO article_contents (
            article_id, content, toc, documents, seo_title, seo_description, seo_keywords
        )
        SELECT id, content, toc, documents, seo_title, seo_description, seo_keywords
        FROM articles
    """)

    for column in ("content", "toc", "documents", "seo_title", "seo_description", "seo_keywords"):
        op.drop_column("articles", column)


def downgrade() -> None:
    """Вернуть содержимое в прежнюю таблицу."""

    op.execute("LOCK TABLE articles, article_contents IN ACCESS EXCLUSIVE MODE")
    op.add_column("articles", sa.Column("content", sa.Text(), nullable=True))
    op.add_column("articles", sa.Column("toc", postgresql.JSONB(), nullable=True))
    op.add_column("articles", sa.Column("documents", postgresql.JSONB(), nullable=True, server_default=sa.text("'[]'")))
    op.add_column("articles", sa.Column("seo_title", sa.String(255), nullable=True))
    op.add_column("articles", sa.Column("seo_description", sa.String(300), nullable=True))
    op.add_column("articles", sa.Column("seo_keywords", sa.String(500), nullable=True))
    op.execute("""
        UPDATE articles SET
            content = article_contents.content,
            toc = article_contents.toc,
            documents = article_contents.documents,
            seo_title = article_contents.seo_title,
            seo_description = article_contents.seo_description,
            seo_keywords = article_contents.seo_keywords
        FROM article_contents WHERE article_contents.article_id = articles.id
    """)

    for column in ("content", "toc", "documents"):
        op.alter_column("articles", column, nullable=False)

    op.drop_table("article_contents")

