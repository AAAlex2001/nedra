"""Проверка данных заявки эксперта по справочнику аттестации."""

from app.services.experts.catalog import AREA_BY_CODE, CATEGORIES, DIRECTION_CODES, OBJECT_BY_CODE
from app.services.experts.exceptions import InvalidCertificateError, InvalidDirectionError


def validate_directions(codes: list[str]) -> None:
    """Все направления должны быть из справочника, без повторов."""

    if len(codes) != len(set(codes)):
        raise InvalidDirectionError("Направления повторяются")

    for code in codes:
        if code not in DIRECTION_CODES:
            raise InvalidDirectionError(f"Неизвестное направление: {code}")


def validate_certificate(area_code: str, object_code: str, category: int) -> None:
    """Область, объект и категория должны существовать, а объект — выдаваться по этой области."""

    area = AREA_BY_CODE.get(area_code)
    if area is None:
        raise InvalidCertificateError(f"Неизвестная область аттестации: {area_code}")

    if object_code not in OBJECT_BY_CODE:
        raise InvalidCertificateError(f"Неизвестный объект экспертизы: {object_code}")

    if object_code not in area.objects:
        label = OBJECT_BY_CODE[object_code].label
        raise InvalidCertificateError(f"По области {area_code} не выдаётся удостоверение {label}")

    if category not in CATEGORIES:
        raise InvalidCertificateError(f"Категория должна быть от 1 до 3, получено {category}")
