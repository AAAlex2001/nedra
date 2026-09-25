from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.expertise import ContractKind, ExpertiseResult, ExpertiseStatus
from app.models.payment import PaymentStatus


Deadline = Literal["today", "three_days", "week", "any"]


class ExpertiseCompanyInSchema(BaseModel):
    """Реквизиты заказчика для договора, счёта и акта."""

    full_name: str = Field(
        ..., min_length=3, max_length=500,
        description="Полное наименование: Общество с ограниченной ответственностью «Ромашка»",
    )
    name: str = Field(
        ..., min_length=2, max_length=255, description="Сокращённое наименование: ООО «Ромашка»"
    )
    inn: str = Field(..., min_length=10, max_length=12, description="ИНН")
    kpp: str | None = Field(None, max_length=9, description="КПП, у предпринимателя его нет")
    ogrn: str = Field(..., min_length=13, max_length=20, description="ОГРН или ОГРНИП")
    address: str = Field(..., min_length=5, max_length=500, description="Юридический адрес")
    bank: str = Field(..., min_length=2, max_length=255, description="Название банка")
    bic: str = Field(..., min_length=9, max_length=12, description="БИК")
    account: str = Field(..., min_length=20, max_length=30, description="Расчётный счёт")
    corr_account: str = Field(..., min_length=20, max_length=30, description="Корреспондентский счёт")
    signer_position: str = Field(
        ..., min_length=2, max_length=255, description="Должность подписанта: Генеральный директор"
    )
    signer_name: str = Field(
        ..., min_length=3, max_length=255, description="ФИО подписанта: Иванов Иван Иванович"
    )
    signer_genitive: str = Field(
        ..., min_length=3, max_length=500,
        description="В лице кого: генерального директора Иванова Ивана Ивановича",
    )
    signer_basis: str = Field(
        "Устава", min_length=2, max_length=255, description="На основании чего действует"
    )


class ExpertiseCompanySchema(ExpertiseCompanyInSchema):
    """Реквизиты заказчика в заявке."""

    model_config = ConfigDict(from_attributes=True)


class ExpertiseInSchema(BaseModel):
    """Заявка на экспертизу.

    Объект, область и требования к эксперту заказчик указывает, если знает их,
    незаполненные поля уточняет эксперт. Наименование документации и реквизиты
    обязательны: по ним составляется договор.
    """

    object_name: str = Field(
        ..., min_length=2, max_length=500, description="Наименование документации, как на титуле"
    )
    company: ExpertiseCompanyInSchema
    contract_kind: ContractKind | None = Field(
        None, description="Вид договора, если заказчик знает вид проекта"
    )
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
    object_name: str | None = None
    contract_kind: ContractKind | None = None
    company: ExpertiseCompanySchema | None = None
    comment: str | None
    status: ExpertiseStatus
    price: Decimal | None
    created_at: datetime


class ExpertiseAcceptSchema(BaseModel):
    """Эксперт берёт заявку. Вид договора указывает, если заказчик его не выбрал."""

    contract_kind: ContractKind | None = Field(None, description="Вид договора")


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
    object_name: str | None = None
    contract_kind: ContractKind | None = None
    company: ExpertiseCompanySchema | None = None
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
