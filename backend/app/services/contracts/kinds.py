"""Виды договора и их связь с объектами экспертизы.

Договоры отличаются только предметом в пункте 1.1. Для КЛ и КЛ/ТП предмет
зависит от проекта, поэтому вид выбирает заказчик, а если он не знает —
эксперт, когда берёт заявку. Для остальных объектов вид однозначен.
"""

from app.models.expertise import ContractKind
from app.services.expertise.exceptions import InvalidExpertiseError

SUBJECTS = {
    ContractKind.JUSTIFICATION: "обоснования безопасности ОПО",
    ContractKind.REEQUIPMENT: "документации на техническое перевооружение ОПО",
    ContractKind.CONSERVATION: "документации на консервацию ОПО",
    ContractKind.LIQUIDATION: "документации на ликвидацию ОПО",
    ContractKind.DECLARATION: "декларации промышленной безопасности",
}

KINDS_BY_OBJECT = {
    "kl": (ContractKind.CONSERVATION, ContractKind.LIQUIDATION),
    "tp": (ContractKind.REEQUIPMENT,),
    "kl_tp": (ContractKind.CONSERVATION, ContractKind.LIQUIDATION, ContractKind.REEQUIPMENT),
    "d": (ContractKind.DECLARATION,),
    "ob": (ContractKind.JUSTIFICATION,),
}


def allowed_kinds(object_code: str | None) -> tuple[ContractKind, ...]:
    """Виды договора, подходящие объекту. Объект неизвестен — подходит любой."""

    if object_code is None:
        return tuple(ContractKind)

    return KINDS_BY_OBJECT.get(object_code, tuple(ContractKind))


def resolve_kind(object_code: str | None, chosen: str | None) -> ContractKind | None:
    """Вид договора для заявки или None, если выбирать ещё предстоит.

    Выбранный вид должен подходить объекту. Если объекту подходит ровно один
    вид, он ставится сам. Бросает InvalidExpertiseError.
    """

    allowed = allowed_kinds(object_code)

    if chosen is not None:
        if chosen not in allowed:
            raise InvalidExpertiseError("Вид договора не подходит объекту экспертизы")
        return ContractKind(chosen)

    if len(allowed) == 1:
        return allowed[0]

    return None
