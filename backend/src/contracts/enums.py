"""Виды договоров."""

from enum import StrEnum


class ContractKind(StrEnum):
    """Предмет договора."""

    JUSTIFICATION = "justification"
    REEQUIPMENT = "reequipment"
    CONSERVATION = "conservation"
    LIQUIDATION = "liquidation"
    DECLARATION = "declaration"
    AUDIT = "audit"


class CustomerType(StrEnum):
    """Сторона договора."""

    LEGAL = "legal"
    ENTREPRENEUR = "entrepreneur"
    INDIVIDUAL = "individual"
