"""Тариф на аудит СУПБ лежит в общей таблице тарифов отдельной парой кодов.

У аудита нет области аттестации и объекта экспертизы, цена одна на всю услугу.
"""

AUDIT_TARIFF_AREA = "audit"
AUDIT_TARIFF_OBJECT = "supb"


def is_audit_tariff(area_code: str, object_code: str) -> bool:
    """Пара кодов — это тариф на аудит, а не на экспертизу."""

    return area_code == AUDIT_TARIFF_AREA and object_code == AUDIT_TARIFF_OBJECT
