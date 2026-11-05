"""Ошибки рассмотрения заявок экспертов."""


class ExpertApplicationNotFoundError(Exception):
    """Заявка эксперта не найдена."""


class ExpertApplicationAlreadyReviewedError(Exception):
    """Заявка уже рассмотрена."""
