"""Проверка заявки на экспертизу по справочнику аттестации."""

from app.services.experts.catalog import (
    AREA_BY_CODE,
    CATEGORIES,
    HAZARD_CLASS_CATEGORY,
    OBJECT_BY_CODE,
)
from app.services.expertise.exceptions import InvalidExpertiseError


def validate_pair(object_code: str, area_code: str) -> None:
    """Объект и область должны быть в справочнике, а объект — выдаваться по этой области."""

    area = AREA_BY_CODE.get(area_code)
    if area is None:
        raise InvalidExpertiseError(f"Неизвестная область аттестации: {area_code}")

    if object_code not in OBJECT_BY_CODE:
        raise InvalidExpertiseError(f"Неизвестный объект экспертизы: {object_code}")

    if object_code not in area.objects:
        label = OBJECT_BY_CODE[object_code].label
        raise InvalidExpertiseError(f"По области {area_code} экспертиза {label} не проводится")


def resolve_category(hazard_class: int | None, expert_category: int | None) -> int:
    """Определить требуемую категорию эксперта.

    Заказчик указывает либо класс опасности объекта, либо категорию напрямую.
    Класс важнее: если указан, категория берётся из справочника.
    """

    if hazard_class is not None:
        category = HAZARD_CLASS_CATEGORY.get(hazard_class)
        if category is None:
            raise InvalidExpertiseError(f"Класс опасности должен быть от 1 до 4, получено {hazard_class}")
        return category

    if expert_category is None:
        raise InvalidExpertiseError("Укажите класс опасности объекта или категорию эксперта")

    if expert_category not in CATEGORIES:
        raise InvalidExpertiseError(f"Категория должна быть от 1 до 3, получено {expert_category}")

    return expert_category
