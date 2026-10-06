from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from app.models.expertise import CustomerType
from app.schemas.expertise import (
    Deadline,
    ExpertiseCompanyInSchema,
    ExpertiseIndividualInSchema,
)


class AuditInSchema(BaseModel):
    """Заявка на аудит СУПБ.

    Наименование — организация или опасный производственный объект, который
    проверяется: оно попадает в договор и отчёт. Цену предлагает заказчик.
    Юрлицо присылает реквизиты в company, физлицо — паспортные данные в individual.
    """

    object_name: str = Field(
        ..., min_length=2, max_length=500,
        description="Что проверяем: организация или опасный производственный объект",
    )
    price: Decimal = Field(
        ..., gt=0, max_digits=10, decimal_places=2, description="Цена, которую предлагает заказчик"
    )
    customer_type: CustomerType = Field(
        CustomerType.LEGAL, description="legal — юрлицо, оплата по счёту; individual — физлицо, картой"
    )
    company: ExpertiseCompanyInSchema | None = None
    individual: ExpertiseIndividualInSchema | None = None
    deadline: Deadline | None = Field(
        None, description="Желаемый срок: today, three_days, week или any"
    )
    comment: str | None = Field(None, max_length=4000, description="Комментарий заказчика")

    @model_validator(mode="after")
    def require_customer_data(self) -> "AuditInSchema":
        """Юрлицу нужны реквизиты, физлицу — паспортные данные."""

        if self.customer_type == CustomerType.LEGAL and self.company is None:
            raise ValueError("Укажите реквизиты организации")

        if self.customer_type == CustomerType.INDIVIDUAL and self.individual is None:
            raise ValueError("Укажите данные физического лица")

        return self


class AuditChecklistItemSchema(BaseModel):
    """Пункт перечня документов для аудита."""

    number: int
    title: str
