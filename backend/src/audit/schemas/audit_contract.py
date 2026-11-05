"""Договор аудита."""

from datetime import datetime

from pydantic import BaseModel

from src.contracts.enums import ContractKind
from src.contracts.models.contract import Contract


class AuditContractResponse(BaseModel):
    """Вид договора и подтверждение заказчика."""

    id: int  # Номер записи договора.
    kind: ContractKind | None  # Выбранный вид договора.
    confirmed_at: datetime | None  # Дата подтверждения заказчиком.

    @classmethod
    def from_model(cls, *, contract: Contract) -> "AuditContractResponse":
        """Подготовить сведения о договоре."""

        return cls(
            id=contract.id,
            kind=contract.kind,
            confirmed_at=contract.confirmed_at,
        )
