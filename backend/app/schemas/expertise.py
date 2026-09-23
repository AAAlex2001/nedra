from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.expertise import ExpertiseResult, ExpertiseStatus
from app.models.payment import PaymentStatus


Deadline = Literal["today", "three_days", "week", "any"]


class ExpertiseInSchema(BaseModel):
    """Заявка на экспертизу.

    Обязательна только документация: объект, область и требования к эксперту
    заказчик указывает, если знает их. Незаполненные поля уточняет эксперт.
    """

    object_code: str | None = Field(
        None, max_length=8, description="Объект экспертизы: kl, tp, kl_tp, d, ob"
    )
    area_code: str | None = Field(
        None, max_length=8, description="Область аттестации, например Э1"
    )
    hazard_class: int | None = Field(None, ge=1, le=4, description="Класс опасности ОПО")
    expert_category: int | None = Field(None, ge=1, le=3, description="Категория эксперта")
    deadline: Deadline | None = Field(
        None, description="Желаемый срок: today, three_days, week или any"
    )
    comment: str | None = Field(None, max_length=4000, description="Комментарий заказчика")


class ExpertiseDocumentSchema(BaseModel):
    """Файл экспертизы. Путь на диске наружу не отдаём."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    kind: str
    original_name: str
    size: int
    content_type: str
    created_at: datetime


class ExpertiseAdminSchema(BaseModel):
    """Заявка в админке: коротко и с именами сторон."""

    id: int
    customer_id: int
    customer_name: str
    expert_id: int | None
    expert_name: str | None
    object_code: str | None
    area_code: str | None
    hazard_class: int | None
    expert_category: int | None
    deadline: Deadline | None = None
    comment: str | None
    status: ExpertiseStatus
    price: Decimal | None
    created_at: datetime


class ExpertiseAdminUpdateSchema(BaseModel):
    """Что админ правит в заявке: статус и стоимость."""

    status: ExpertiseStatus
    price: Decimal | None = Field(None, gt=0, max_digits=10, decimal_places=2)


class ExpertiseRemarkSchema(BaseModel):
    """Замечания эксперта: текст, файлы и дата, когда заказчик прислал исправления."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str | None
    response_text: str | None
    created_at: datetime
    resolved_at: datetime | None
    documents: list[ExpertiseDocumentSchema]


class ExpertiseInvoiceSchema(BaseModel):
    """Неоплаченный счёт заявки: по нему заказчик жмёт «Я оплатил» прямо в карточке."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    number: str
    amount: Decimal
    reported_at: datetime | None
    paid_at: datetime | None


class ExpertisePaymentSchema(BaseModel):
    """Платёж по этапу экспертизы: сумма, статус и ссылка на оплату, пока она есть."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: Decimal
    status: PaymentStatus
    confirmation_url: str | None
    paid_at: datetime | None


class ExpertiseOutSchema(BaseModel):
    """Экспертиза для кабинета заказчика и эксперта."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    customer_name: str
    expert_id: int | None
    expert_name: str | None
    object_code: str | None
    area_code: str | None
    hazard_class: int | None
    expert_category: int | None
    deadline: Deadline | None = None
    comment: str | None
    status: ExpertiseStatus
    result: ExpertiseResult | None
    price: Decimal | None
    advance_payment: ExpertisePaymentSchema | None
    final_payment: ExpertisePaymentSchema | None
    invoice: ExpertiseInvoiceSchema | None
    created_at: datetime
    expert_ready_at: datetime | None
    contract_at: datetime | None
    advance_paid_at: datetime | None
    conclusion_ready_at: datetime | None
    final_paid_at: datetime | None
    sent_at: datetime | None
    accepted_at: datetime | None
    documents: list[ExpertiseDocumentSchema]
    remarks: list[ExpertiseRemarkSchema]
