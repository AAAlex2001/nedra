"""Подача заявки на экспертизу."""

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.contracts.enums import ContractKind, CustomerType
from src.contracts.schemas.company import CompanyDetails
from src.expertise.enums import ExpertiseResult, ExpertiseStatus
from src.expertise.models.expertise import Expertise
from src.expertise.schemas.expertise_conditions import ExpertiseConditionsResponse
from src.expertise.schemas.expertise_dates import ExpertiseDatesResponse
from src.expertise.schemas.expertise_object import ExpertiseObjectResponse
from src.expertise.schemas.individual import IndividualDetails


class CreateExpertiseRequest(BaseModel):
    """Документация, условия и реквизиты заказчика."""

    model_config = ConfigDict(str_strip_whitespace=True)
    object_name: str = Field(
        min_length=2,
        max_length=500,
    )
    price: Decimal = Field(
        gt=0,
        max_digits=10,
        decimal_places=2,
    )
    customer_type: CustomerType = CustomerType.LEGAL
    company: CompanyDetails | None = None
    individual: IndividualDetails | None = None
    contract_kind: ContractKind | None = None
    object_code: str | None = Field(
        default=None,
        max_length=8,
    )
    area_code: str | None = Field(
        default=None,
        max_length=8,
    )
    hazard_class: int | None = Field(
        default=None,
        ge=1,
        le=4,
    )
    expert_category: int | None = Field(
        default=None,
        ge=1,
        le=3,
    )
    deadline: Literal["today", "three_days", "week", "any"] | None = None
    comment: str | None = Field(
        default=None,
        max_length=4000,
    )

    @model_validator(mode="after")
    def validate_customer_details(self) -> "CreateExpertiseRequest":
        """Проверить наличие реквизитов заказчика."""

        if self.customer_type == CustomerType.INDIVIDUAL:
            if self.individual is None:
                raise ValueError("Укажите данные физического лица")
        elif self.company is None:
            raise ValueError("Укажите реквизиты организации")

        return self


class CreateExpertiseResponse(BaseModel):
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
    def from_model(cls, *, expertise: Expertise) -> "CreateExpertiseResponse":
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
