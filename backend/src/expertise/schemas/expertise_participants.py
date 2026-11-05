"""Участники экспертизы."""

from pydantic import BaseModel

from src.contracts.enums import CustomerType
from src.expertise.schemas.expertise_company import ExpertiseCompanyResponse
from src.expertise.schemas.individual import IndividualResponse
from src.users.models.user import User


class ExpertiseParticipantResponse(BaseModel):
    """Имя участника."""

    id: int  # Номер пользователя.
    full_name: str  # Имя пользователя.

    @classmethod
    def from_model(cls, *, user: User) -> "ExpertiseParticipantResponse":
        """Подготовить сведения об участнике."""

        return cls(
            id=user.id,
            full_name=user.full_name,
        )


class ExpertiseParticipantsResponse(BaseModel):
    """Заказчик, его реквизиты и назначенный эксперт."""

    customer: ExpertiseParticipantResponse  # Заказчик.
    expert: ExpertiseParticipantResponse | None  # Назначенный эксперт.
    customer_type: CustomerType  # Организация, ИП или физлицо.
    company: ExpertiseCompanyResponse | None  # Реквизиты организации или ИП.
    individual: IndividualResponse | None  # Реквизиты физлица.
