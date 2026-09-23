"""Проверка заявки на экспертизу по справочнику аттестации.

Заказчик может не знать объект экспертизы, область аттестации и требования
к эксперту — тогда соответствующие поля приходят пустыми. Проверяем только то,
что заказчик указал: неизвестный код — ошибка, отсутствие кода — нет.
"""

from app.services.experts.catalog import (
    AREA_BY_CODE,
    CATEGORIES,
    HAZARD_CLASS_CATEGORY,
    OBJECT_BY_CODE,
)
from app.services.expertise.exceptions import InvalidExpertiseError


def validate_pair(object_code: str | None, area_code: str | None) -> None:
    """Проверить указанные коды по справочнику.

    Если оба указаны — объект должен выдаваться по этой области. Если указан
    только один или ни одного, пару не проверяем: её определит эксперт.
    """

    if area_code is not None and area_code not in AREA_BY_CODE:
        raise InvalidExpertiseError(f"Неизвестная область аттестации: {area_code}")

    if object_code is not None and object_code not in OBJECT_BY_CODE:
        raise InvalidExpertiseError(f"Неизвестный объект экспертизы: {object_code}")

    if object_code is None or area_code is None:
        return

    area = AREA_BY_CODE[area_code]
    if object_code not in area.objects:
        label = OBJECT_BY_CODE[object_code].label
        raise InvalidExpertiseError(f"По области {area_code} экспертиза {label} не проводится")


def resolve_category(hazard_class: int | None, expert_category: int | None) -> int | None:
    """Определить требуемую категорию эксперта.

    Заказчик указывает либо класс опасности объекта, либо категорию напрямую.
    Класс важнее: если указан, категория берётся из справочника. Если не указано
    ничего, требований к категории нет — заявку сможет взять любой эксперт.
    """

    if hazard_class is not None:
        category = HAZARD_CLASS_CATEGORY.get(hazard_class)
        if category is None:
            raise InvalidExpertiseError(
                f"Класс опасности должен быть от 1 до 4, получено {hazard_class}"
            )
        return category

    if expert_category is None:
        return None

    if expert_category not in CATEGORIES:
        raise InvalidExpertiseError(
            f"Категория должна быть от 1 до 3, получено {expert_category}"
        )

    return expert_category
