"""Условия экспертизы."""

from decimal import Decimal

from pydantic import BaseModel

from src.expertise.models.expertise import Expertise


class ExpertiseConditionsResponse(BaseModel):
    """Стоимость и пожелания заказчика."""

    price: Decimal | None  # Стоимость в рублях.
    deadline: str | None  # Желаемый срок выполнения.
    comment: str | None  # Комментарий заказчика.

    @classmethod
    def from_model(cls, *, expertise: Expertise) -> "ExpertiseConditionsResponse":
        """Условия экспертизы."""

        return cls(
            price=expertise.price,
            deadline=expertise.deadline,
            comment=expertise.comment,
        )
