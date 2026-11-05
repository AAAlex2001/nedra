"""Состояния регистрации эксперта."""

from enum import StrEnum


class ApplicationStatus(StrEnum):
    """Статус заявки эксперта."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
