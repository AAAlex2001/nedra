"""Принятие экспертизы."""

from pydantic import BaseModel

from src.contracts.enums import ContractKind


class AcceptExpertiseRequest(BaseModel):
    """Вид договора, выбранный экспертом."""

    contract_kind: ContractKind | None = None
