"""Разделы и порядок публикаций."""

from enum import StrEnum


class ArticleSection(StrEnum):
    """Раздел сайта."""

    BLOG = "blog"
    NEWS = "news"


class ArticleSort(StrEnum):
    """Сортировка опубликованных статей."""

    NEWEST = "newest"
    OLDEST = "oldest"
    VIEWS_DESC = "views_desc"
    VIEWS_ASC = "views_asc"
    LIKES_DESC = "likes_desc"
    LIKES_ASC = "likes_asc"
    DISLIKES_DESC = "dislikes_desc"
    DISLIKES_ASC = "dislikes_asc"


class AdminArticleSort(StrEnum):
    """Сортировка редакторского списка."""

    NEW = "new"
    VIEWS = "views"
    LIKES = "likes"
    DISLIKES = "dislikes"
