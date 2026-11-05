"""Проверка условий экспертизы."""

from src.contracts.enums import ContractKind
from src.contracts.options import CONTRACT_KINDS_BY_OBJECT, EXPERTISE_CONTRACT_KINDS
from src.expertise.exceptions import InvalidExpertiseError
from src.users.options import AREA_BY_CODE, HAZARD_CLASS_CATEGORY, OBJECT_BY_CODE


def validate_expertise_codes(
    *,
    object_code: str | None,
    area_code: str | None,
) -> None:
    """Проверить объект и область аттестации."""

    if area_code is not None and area_code not in AREA_BY_CODE:
        raise InvalidExpertiseError(f"Неизвестная область аттестации: {area_code}")

    if object_code is not None and object_code not in OBJECT_BY_CODE:
        raise InvalidExpertiseError(f"Неизвестный объект экспертизы: {object_code}")

    if object_code is None or area_code is None:
        return

    if object_code not in AREA_BY_CODE[area_code].objects:
        raise InvalidExpertiseError("Объект не входит в выбранную область аттестации")


def determine_expert_category(
    *,
    hazard_class: int | None,
    expert_category: int | None,
) -> int | None:
    """Определить категорию по классу опасности."""

    if hazard_class is not None:
        return HAZARD_CLASS_CATEGORY[hazard_class]

    return expert_category


def determine_contract_kind(
    *,
    object_code: str | None,
    chosen_kind: ContractKind | None,
) -> ContractKind | None:
    """Подобрать договор по объекту экспертизы."""

    allowed_kinds = CONTRACT_KINDS_BY_OBJECT.get(object_code, EXPERTISE_CONTRACT_KINDS)

    if chosen_kind is not None:
        if chosen_kind not in allowed_kinds:
            raise InvalidExpertiseError("Вид договора не подходит объекту экспертизы")

        return chosen_kind

    if len(allowed_kinds) == 1:
        return allowed_kinds[0]

    return None
