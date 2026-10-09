from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.billing import Invoice


class ExpertiseStatus(StrEnum):
    """Путь экспертизы от подачи документации до приёмки работы.

    new — заявка подана, ждёт эксперта;
    expert_ready — эксперт готов провести экспертизу, ждём согласия заказчика;
    contract — обе стороны согласились, договор считается заключённым, ждём аванс;
    in_progress — аванс оплачен, эксперт работает;
    remarks — эксперт выдал замечания, ждём исправленную документацию;
    conclusion_ready — эксперт сообщил, что заключение готово, ждём остаток;
    paid — остаток оплачен, эксперт подписывает заключение и отправляет;
    sent — заключение отправлено заказчику;
    accepted — заказчик принял работу.

    Только у аудита:
    consultation — заказчику нужна консультация по типу аудита, заявку сначала видит менеджер;
    offer — руководитель группы предложил свою цену, ждём ответа заказчика;
    counter — заказчик понизил цену, ждём ответа руководителя группы;
    plan — аванс оплачен, руководитель группы готовит План аудита;
    plan_review — План отправлен, ждём согласования заказчика.
    """

    NEW = "new"
    CONSULTATION = "consultation"
    OFFER = "offer"
    COUNTER = "counter"
    EXPERT_READY = "expert_ready"
    CONTRACT = "contract"
    PLAN = "plan"
    PLAN_REVIEW = "plan_review"
    IN_PROGRESS = "in_progress"
    REMARKS = "remarks"
    CONCLUSION_READY = "conclusion_ready"
    PAID = "paid"
    SENT = "sent"
    ACCEPTED = "accepted"


class ExpertiseResult(StrEnum):
    """Исход экспертизы: заключение бывает только положительным или отрицательным.

    Замечания — это отдельный этап до заключения, а не его исход.
    """

    POSITIVE = "positive"
    NEGATIVE = "negative"


class ServiceKind(StrEnum):
    """Какую работу заказали: экспертизу промышленной безопасности или аудит СУПБ.

    Оба сервиса идут по одним и тем же шагам: исполнитель берёт заявку, договор,
    аванс, работа с замечаниями, остаток, итоговый документ, приёмка.
    """

    EXPERTISE = "expertise"
    AUDIT = "audit"


class ContractKind(StrEnum):
    """Вид договора по предмету работ. От него зависят текст и исполнитель."""

    JUSTIFICATION = "justification"
    REEQUIPMENT = "reequipment"
    CONSERVATION = "conservation"
    LIQUIDATION = "liquidation"
    DECLARATION = "declaration"
    AUDIT = "audit"


class CustomerType(StrEnum):
    """Кто заказчик. Юрлицо и ИП платят по счёту, физлицо — картой."""

    LEGAL = "legal"
    ENTREPRENEUR = "entrepreneur"
    INDIVIDUAL = "individual"


COMPANY_CUSTOMERS = (CustomerType.LEGAL, CustomerType.ENTREPRENEUR)


def uses_company(customer_type: str) -> bool:
    """Заказчик с реквизитами организации: юрлицо или ИП. Платит по счёту."""

    return customer_type in COMPANY_CUSTOMERS


class Expertise(Base):
    """Заявка заказчика на экспертизу промышленной безопасности.

    Заказчик прикладывает документацию, а объект экспертизы, область аттестации
    и требования к эксперту указывает по желанию: если он их не знает, поля
    остаются пустыми и заявку разбирает эксперт. Цену назначает сам заказчик,
    эксперт берёт заявку, только если согласен с ней. Эксперт назначается позже,
    поэтому expert_id пустой.

    Вид договора выбирает заказчик, а если не знает — эксперт, когда берёт
    заявку. От вида зависит, какая организация выступает исполнителем.
    Реквизиты лежат в company у юрлица и в individual у физлица.

    У аудита в audit_details хранятся сведения о заявителе, масштаб, ОПО, этапы,
    параметры, сроки и бюджет. В offer_price — цена, которую предложил
    руководитель группы, в counter_price — сниженная цена заказчика.
    audit_plan — последняя версия Плана аудита, plan_comment — просьба заказчика
    скорректировать План. Аудиторы группы, кроме руководителя, лежат в team.
    """

    __tablename__ = "expertises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    expert_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )

    service: Mapped[str] = mapped_column(String(16), index=True, default=ServiceKind.EXPERTISE)

    object_code: Mapped[str | None] = mapped_column(String(8), index=True)
    area_code: Mapped[str | None] = mapped_column(String(8), index=True)
    hazard_class: Mapped[int | None] = mapped_column(SmallInteger)
    expert_category: Mapped[int | None] = mapped_column(SmallInteger)

    deadline: Mapped[str | None] = mapped_column(String(16))

    object_name: Mapped[str | None] = mapped_column(String(500))
    contract_kind: Mapped[str | None] = mapped_column(String(16))
    customer_type: Mapped[str] = mapped_column(String(16), default=CustomerType.LEGAL)

    comment: Mapped[str | None] = mapped_column(Text)
    audit_details: Mapped[dict | None] = mapped_column(JSON().with_variant(JSONB, "postgresql"))
    status: Mapped[str] = mapped_column(String(32), index=True, default=ExpertiseStatus.NEW)
    price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    offer_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    counter_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    audit_plan: Mapped[dict | None] = mapped_column(JSON().with_variant(JSONB, "postgresql"))
    plan_comment: Mapped[str | None] = mapped_column(Text)
    result: Mapped[str | None] = mapped_column(String(16))

    advance_payment_id: Mapped[int | None] = mapped_column(
        ForeignKey("payments.id", ondelete="SET NULL")
    )
    final_payment_id: Mapped[int | None] = mapped_column(
        ForeignKey("payments.id", ondelete="SET NULL")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expert_ready_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    contract_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    advance_paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    plan_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    plan_approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    conclusion_ready_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    final_paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    documents: Mapped[list["ExpertiseDocument"]] = relationship(
        back_populates="expertise",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="ExpertiseDocument.id",
    )

    remarks: Mapped[list["ExpertiseRemark"]] = relationship(
        back_populates="expertise",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="ExpertiseRemark.id",
    )

    invoices: Mapped[list["Invoice"]] = relationship(
        back_populates="expertise",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="Invoice.id",
    )

    company: Mapped["ExpertiseCompany | None"] = relationship(
        back_populates="expertise",
        lazy="selectin",
        cascade="all, delete-orphan",
        uselist=False,
    )

    individual: Mapped["ExpertiseIndividual | None"] = relationship(
        back_populates="expertise",
        lazy="selectin",
        cascade="all, delete-orphan",
        uselist=False,
    )

    team: Mapped[list["AuditTeamMember"]] = relationship(
        back_populates="expertise",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="AuditTeamMember.user_id",
    )


class AuditTeamMember(Base):
    """Аудитор в группе по заявке на аудит. Руководитель группы — expert_id заявки."""

    __tablename__ = "audit_team_members"

    expertise_id: Mapped[int] = mapped_column(
        ForeignKey("expertises.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )

    expertise: Mapped["Expertise"] = relationship(back_populates="team")


class ExpertiseIndividual(Base):
    """Данные заказчика-физлица по заявке: попадают в договор и акт."""

    __tablename__ = "expertise_individuals"

    expertise_id: Mapped[int] = mapped_column(
        ForeignKey("expertises.id", ondelete="CASCADE"), primary_key=True
    )

    full_name: Mapped[str] = mapped_column(String(255))
    passport_number: Mapped[str] = mapped_column(String(20))
    passport_issued_by: Mapped[str] = mapped_column(String(500))
    passport_issued_at: Mapped[date] = mapped_column(Date)
    address: Mapped[str] = mapped_column(String(500))

    expertise: Mapped["Expertise"] = relationship(back_populates="individual")


class ExpertiseCompany(Base):
    """Реквизиты заказчика по конкретной заявке.

    Один человек подаёт заявки от разных организаций, поэтому реквизиты живут
    в заявке, а не в профиле. По ним заполняются договор, счёт и акт.
    """

    __tablename__ = "expertise_companies"

    expertise_id: Mapped[int] = mapped_column(
        ForeignKey("expertises.id", ondelete="CASCADE"), primary_key=True
    )

    full_name: Mapped[str] = mapped_column(String(500))
    name: Mapped[str] = mapped_column(String(255))
    inn: Mapped[str] = mapped_column(String(12))
    kpp: Mapped[str | None] = mapped_column(String(9))
    ogrn: Mapped[str] = mapped_column(String(15))
    address: Mapped[str] = mapped_column(String(500))

    bank: Mapped[str] = mapped_column(String(255))
    bic: Mapped[str] = mapped_column(String(9))
    account: Mapped[str] = mapped_column(String(20))
    corr_account: Mapped[str] = mapped_column(String(20))

    signer_position: Mapped[str] = mapped_column(String(255))
    signer_name: Mapped[str] = mapped_column(String(255))
    signer_genitive: Mapped[str] = mapped_column(String(500))
    signer_basis: Mapped[str] = mapped_column(String(255))

    expertise: Mapped["Expertise"] = relationship(back_populates="company")


class ExpertiseRemark(Base):
    """Замечания эксперта по документации: рекомендации по приведению объекта в соответствие.

    Эксперт пишет текст, прикладывает файл или делает и то и другое. Заказчик
    исправляет документацию и отправляет её повторно, тогда замечание считается
    закрытым. Раундов замечаний может быть несколько, поэтому храним их списком.
    """

    __tablename__ = "expertise_remarks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    expertise_id: Mapped[int] = mapped_column(
        ForeignKey("expertises.id", ondelete="CASCADE"), index=True
    )

    text: Mapped[str | None] = mapped_column(Text)
    response_text: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    expertise: Mapped["Expertise"] = relationship(back_populates="remarks")

    documents: Mapped[list["ExpertiseDocument"]] = relationship(
        back_populates="remark",
        lazy="selectin",
        order_by="ExpertiseDocument.id",
    )


class ExpertiseDocument(Base):
    """Файл, приложенный к заявке: документация заказчика или заключение эксперта.

    В аудите заказчик прикладывает документы по перечню, номер пункта
    перечня хранится в item_number.
    """

    __tablename__ = "expertise_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    expertise_id: Mapped[int] = mapped_column(
        ForeignKey("expertises.id", ondelete="CASCADE"), index=True
    )
    remark_id: Mapped[int | None] = mapped_column(
        ForeignKey("expertise_remarks.id", ondelete="CASCADE")
    )
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))

    kind: Mapped[str] = mapped_column(String(32), default="documentation")
    item_number: Mapped[int | None] = mapped_column(SmallInteger)
    file_path: Mapped[str] = mapped_column(String(500))
    original_name: Mapped[str] = mapped_column(String(255))
    size: Mapped[int] = mapped_column(Integer)
    content_type: Mapped[str] = mapped_column(String(128))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    expertise: Mapped["Expertise"] = relationship(back_populates="documents")
    remark: Mapped["ExpertiseRemark | None"] = relationship(back_populates="documents")
