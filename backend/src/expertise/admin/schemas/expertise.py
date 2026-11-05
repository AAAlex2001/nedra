"""Управление заявками экспертизы."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from src.contracts.enums import ContractKind
from src.expertise.enums import ExpertiseStatus


class ExpertiseAdminResponse(BaseModel):
    """Строка списка работ."""

    id: int  # Номер работы.
    status: ExpertiseStatus  # Текущий этап.
    customer_id: int  # Заказчик.
    customer_name: str  # Имя заказчика.
    expert_id: int | None  # Исполнитель.
    expert_name: str | None  # Имя исполнителя.
    object_name: str | None  # Наименование объекта.
    price: Decimal | None  # Стоимость работы.
    created_at: datetime  # Дата подачи.


class UpdateExpertiseRequest(BaseModel):
    """Изменения администратора."""

    status: ExpertiseStatus  # Новый этап работы.
    price: Decimal | None = Field(
        ge=0,
        max_digits=10,
        decimal_places=2,
    )  # Стоимость в рублях.
    expert_id: int | None = Field(ge=1)  # Назначенный исполнитель.
    contract_kind: ContractKind | None = None  # Вид договора.
