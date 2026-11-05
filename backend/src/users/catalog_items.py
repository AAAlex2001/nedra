"""Элементы справочника аттестации."""

from dataclasses import dataclass


@dataclass(
    frozen=True,
    kw_only=True,
)
class Direction:
    """Направление работы."""

    code: str  # Код направления.
    title: str  # Название направления.


@dataclass(
    frozen=True,
    kw_only=True,
)
class ExpertiseObject:
    """Вид объекта экспертизы."""

    code: str  # Код объекта.
    label: str  # Краткое обозначение.
    title: str  # Название объекта.
    description: str  # Пояснение для заказчика.


@dataclass(
    frozen=True,
    kw_only=True,
)
class AttestationArea:
    """Область аттестации."""

    code: str  # Код области.
    title: str  # Название области.
    objects: tuple[str, ...]  # Допустимые виды объектов.
