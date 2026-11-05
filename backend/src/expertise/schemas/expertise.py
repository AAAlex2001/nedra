"""Основные сведения об экспертизе."""

from pydantic import BaseModel

from src.expertise.enums import ExpertiseResult, ExpertiseStatus
from src.expertise.models.expertise import Expertise
from src.expertise.schemas.expertise_conditions import ExpertiseConditionsResponse
from src.expertise.schemas.expertise_dates import ExpertiseDatesResponse
from src.expertise.schemas.expertise_object import ExpertiseObjectResponse


class ExpertiseResponse(BaseModel):
    """Объект, условия и состояние экспертизы."""

    id: int  # Номер экспертизы.
    customer_id: int  # Номер заказчика.
    expert_id: int | None  # Номер назначенного эксперта.
    status: ExpertiseStatus  # Текущий этап.
    result: ExpertiseResult | None  # Результат заключения.
    object: ExpertiseObjectResponse  # Объект и требования к эксперту.
    conditions: ExpertiseConditionsResponse  # Цена, срок и пожелания заказчика.
    dates: ExpertiseDatesResponse  # Даты прохождения этапов.

    @classmethod
    def from_model(cls, *, expertise: Expertise) -> "ExpertiseResponse":
        """Подготовить сведения об экспертизе."""

        return cls(
            id=expertise.id,
            customer_id=expertise.customer_id,
            expert_id=expertise.expert_id,
            status=expertise.status,
            result=expertise.result,
            object=ExpertiseObjectResponse.from_model(expertise=expertise),
            conditions=ExpertiseConditionsResponse.from_model(expertise=expertise),
            dates=ExpertiseDatesResponse.from_model(expertise=expertise),
        )
