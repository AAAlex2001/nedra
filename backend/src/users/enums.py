"""Роли пользователей."""

from enum import StrEnum


class UserRole(StrEnum):
    """Роль пользователя."""

    CUSTOMER = "customer"
    EXPERT = "expert"
