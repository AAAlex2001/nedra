from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.models.expertise import COMPANY_CUSTOMERS, CustomerType
from app.schemas.audit_details import AuditDetailsSchema
from app.schemas.expertise import ExpertiseCompanyInSchema
from app.services.audit.options import MIN_AUDIT_PRICE

PRICE_FIELD = Field(..., max_digits=10, decimal_places=2)


class AuditInSchema(BaseModel):
    """Заявка на аудит СУПБ.

    Что проверяем, описано в details. Цену заказчик указывает сам — не ниже
    100 000 ₽ — или оставляет бюджет неустановленным, тогда её выставит
    руководитель аудиторской группы. Заказчик — юрлицо или ИП, реквизиты в company.
    """

    details: AuditDetailsSchema
    price: Decimal | None = Field(
        None, max_digits=10, decimal_places=2, description="Цена заказчика, не ниже 100 000 ₽"
    )
    customer_type: CustomerType = Field(
        CustomerType.LEGAL, description="legal — юрлицо, entrepreneur — ИП"
    )
    company: ExpertiseCompanyInSchema
    comment: str | None = Field(None, max_length=4000, description="Комментарий заказчика")

    @model_validator(mode="after")
    def check_customer_and_price(self) -> "AuditInSchema":
        """Аудит заказывает организация или ИП, своя цена — не ниже минимальной."""

        if self.customer_type not in COMPANY_CUSTOMERS:
            raise ValueError("Аудит заказывает юридическое лицо или индивидуальный предприниматель")

        custom = self.details.budget.mode == "custom"

        if custom and self.price is None:
            raise ValueError("Укажите сумму")

        if not custom and self.price is not None:
            raise ValueError("Бюджет не установлен: сумму не указывают")

        if self.price is not None and self.price < MIN_AUDIT_PRICE:
            raise ValueError("Стоимость аудита — не менее 100 000 ₽")

        return self


class AuditPriceSchema(BaseModel):
    """Цена в торге: предложение руководителя группы или сниженная цена заказчика."""

    price: Decimal = PRICE_FIELD

    @model_validator(mode="after")
    def check_minimum(self) -> "AuditPriceSchema":
        """Ниже минимальной цены торговаться нельзя."""

        if self.price < MIN_AUDIT_PRICE:
            raise ValueError("Стоимость аудита — не менее 100 000 ₽")

        return self


class AuditOfferAnswerSchema(BaseModel):
    """Ответ заказчика на цену аудитора: принять, понизить или отказаться."""

    answer: Literal["accept", "counter", "decline"]
    price: Decimal | None = Field(None, max_digits=10, decimal_places=2)

    @model_validator(mode="after")
    def check_counter(self) -> "AuditOfferAnswerSchema":
        """Сниженная цена обязательна при понижении и не ниже минимальной."""

        if self.answer == "counter" and self.price is None:
            raise ValueError("Укажите свою цену")

        if self.price is not None and self.price < MIN_AUDIT_PRICE:
            raise ValueError("Стоимость аудита — не менее 100 000 ₽")

        return self


class AuditCounterAnswerSchema(BaseModel):
    """Ответ руководителя группы на сниженную цену заказчика."""

    accept: bool


class AuditTeamSchema(BaseModel):
    """Аудиторы, которых руководитель включает в группу."""

    user_ids: list[int] = Field(default_factory=list, max_length=20)


class AuditPlanChangesSchema(BaseModel):
    """Просьба заказчика скорректировать План аудита."""

    comment: str = Field(..., min_length=3, max_length=4000)


class AuditChecklistItemSchema(BaseModel):
    """Пункт перечня документов для аудита."""

    number: int
    title: str
