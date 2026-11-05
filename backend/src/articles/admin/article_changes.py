"""Изменения карточки и содержимого."""

from datetime import UTC, datetime

from src.articles.admin.schemas.article import UpdateArticleRequest
from src.articles.content import prepare_content
from src.articles.models.article import Article
from src.articles.models.article_content import ArticleContent


def update_article_card(
    *,
    article: Article,
    payload: UpdateArticleRequest,
) -> None:
    """Применить поля карточки."""

    if payload.title is not None:
        article.title = payload.title

    if payload.section is not None:
        article.section = payload.section

    if "description" in payload.model_fields_set:
        article.description = payload.description

    if "cover_image" in payload.model_fields_set:
        article.cover_image = payload.cover_image

    if payload.published is True and article.published_at is None:
        article.published_at = datetime.now(UTC)
    elif payload.published is False:
        article.published_at = None

    if payload.published_at is not None:
        article.published_at = payload.published_at

    article.updated_at = datetime.now(UTC)


def update_article_content(
    *,
    content: ArticleContent,
    payload: UpdateArticleRequest,
) -> None:
    """Применить текст и поисковое описание."""

    if payload.content is not None:
        prepared = prepare_content(raw_html=payload.content)
        content.content = prepared.html
        content.toc = prepared.headings

    if payload.documents is not None:
        content.documents = [document.to_record() for document in payload.documents]

    if "seo_title" in payload.model_fields_set:
        content.seo_title = payload.seo_title

    if "seo_description" in payload.model_fields_set:
        content.seo_description = payload.seo_description

    if "seo_keywords" in payload.model_fields_set:
        content.seo_keywords = payload.seo_keywords
