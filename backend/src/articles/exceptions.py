"""Ошибки публикаций."""


class ArticleNotFoundError(Exception):
    """Публикация не найдена."""


class TagNotFoundError(Exception):
    """Тег не найден."""


class ArticleConflictError(Exception):
    """Адрес публикации или тега занят."""
