"""Публикация статьи: общая логика для создания и обновления."""

from sqlalchemy import func

from app.models.article import Article


def apply_published(article: Article, published: bool | None) -> None:
    """Опубликовать статью, если она ещё не опубликована, или снять с публикации.

    Дату публикации ставит база, чтобы она совпадала по часам с created_at.
    """

    if published and article.published_at is None:
        article.published_at = func.now()
    elif published is False:
        article.published_at = None
