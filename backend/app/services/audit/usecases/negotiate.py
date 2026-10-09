"""Торг по цене аудита: руководитель группы предлагает цену, заказчик отвечает.

Круг один: аудитор предложил → заказчик принял, понизил или отказался → на
понижение аудитор соглашается или отказывается. Если не договорились, заявка
возвращается в общий список, и её может взять другой руководитель группы.
Ниже 100 000 ₽ цена не опускается — это проверяет схема запроса.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Literal

from app.models.expertise import Expertise, ExpertiseStatus, ServiceKind
from app.models.notification import Notification
from app.models.user import User
from app.schemas.audit_details import AuditDetailsSchema
from app.services.experts.repo import ExpertProfileRepository
from app.services.expertise.exceptions import (
    ExpertiseAccessError,
    ExpertiseStateError,
    InvalidExpertiseError,
)
from app.services.expertise.money import format_rub
from app.services.expertise.repo import ExpertiseRepository
from app.services.notifications.repo import NotificationRepository

OfferAnswer = Literal["accept", "counter", "decline"]


def negotiable(audit: Expertise) -> bool:
    """Готов ли заказчик обсуждать стоимость."""

    details = AuditDetailsSchema.model_validate(audit.audit_details)

    return details.budget.negotiation != "no"


def release(audit: Expertise) -> None:
    """Вернуть заявку в общий список: руководитель снят, предложения обнулены."""

    audit.status = ExpertiseStatus.NEW
    audit.expert_id = None
    audit.offer_price = None
    audit.counter_price = None
    audit.expert_ready_at = None


def agree(audit: Expertise, price: Decimal) -> None:
    """Стороны сошлись на цене: дальше договор, как после «Готов провести»."""

    audit.price = price
    audit.offer_price = None
    audit.counter_price = None
    audit.expert_ready_at = datetime.now(timezone.utc)
    audit.status = ExpertiseStatus.EXPERT_READY


def notify(user_id: int, audit: Expertise, text: str) -> Notification:
    """Уведомление участнику торга."""

    return Notification(user_id=user_id, expertise_id=audit.id, text=text)


class ProposePriceUseCase:
    """Руководитель группы предлагает свою цену.

    Это возможно, если заказчик не установил бюджет или готов обсуждать
    стоимость. При строго фиксированном бюджете заявку берут только по цене заказчика.
    """

    def __init__(
        self,
        expertises: ExpertiseRepository,
        profiles: ExpertProfileRepository,
        notifications: NotificationRepository,
    ) -> None:
        self.expertises = expertises
        self.profiles = profiles
        self.notifications = notifications

    async def execute(self, lead: User, audit: Expertise, price: Decimal) -> Expertise:
        """Бросает InvalidExpertiseError, ExpertiseStateError, ExpertiseAccessError."""

        if audit.service != ServiceKind.AUDIT:
            raise InvalidExpertiseError("Предложить цену можно только по заявке на аудит")

        if audit.status != ExpertiseStatus.NEW or audit.expert_id is not None:
            raise ExpertiseStateError("Заявку уже взял другой аудитор")

        if not await self.profiles.is_audit_lead(lead.id):
            raise ExpertiseAccessError(
                "Брать заявки на аудит может только руководитель аудиторской группы"
            )

        if audit.price is not None and not negotiable(audit):
            raise ExpertiseStateError("Заказчик не готов обсуждать цену: возьмите заявку по его цене")

        audit.expert_id = lead.id
        audit.offer_price = price
        audit.counter_price = None
        audit.status = ExpertiseStatus.OFFER

        self.notifications.add_all(
            [
                notify(
                    audit.customer_id,
                    audit,
                    f"Аудитор НПИ «Недра» предложил цену {format_rub(price)} по заявке №{audit.id}",
                )
            ]
        )

        return await self.expertises.save(audit)


class AnswerOfferUseCase:
    """Заказчик принимает цену аудитора, понижает её или отказывается."""

    def __init__(
        self, expertises: ExpertiseRepository, notifications: NotificationRepository
    ) -> None:
        self.expertises = expertises
        self.notifications = notifications

    async def execute(
        self,
        customer: User,
        audit: Expertise,
        answer: OfferAnswer,
        price: Decimal | None = None,
    ) -> Expertise:
        """Бросает ExpertiseAccessError, ExpertiseStateError, InvalidExpertiseError."""

        if audit.customer_id != customer.id:
            raise ExpertiseAccessError("Ответить на предложение может только заказчик этой заявки")

        if audit.status != ExpertiseStatus.OFFER or audit.offer_price is None:
            raise ExpertiseStateError("Предложения по цене сейчас нет")

        lead_id = audit.expert_id

        if answer == "accept":
            text = self.accept(audit)
        elif answer == "counter":
            text = self.counter(audit, price)
        else:
            text = self.decline(audit)

        self.notifications.add_all([notify(lead_id, audit, text)])

        return await self.expertises.save(audit)

    def accept(self, audit: Expertise) -> str:
        """Заказчик согласен с ценой аудитора. Возвращает текст уведомления аудитору."""

        offer = audit.offer_price
        agree(audit, offer)

        return f"Заказчик принял цену {format_rub(offer)} по заявке №{audit.id}, ждём подписания договора"

    def counter(self, audit: Expertise, price: Decimal | None) -> str:
        """Заказчик предлагает цену ниже. Бросает ExpertiseStateError и InvalidExpertiseError."""

        if not negotiable(audit):
            raise ExpertiseStateError("Вы указали, что бюджет фиксирован: примите цену или откажитесь")

        if price is None or price >= audit.offer_price:
            raise InvalidExpertiseError("Предложите цену ниже цены аудитора")

        audit.counter_price = price
        audit.status = ExpertiseStatus.COUNTER

        return f"Заказчик предложил {format_rub(price)} вместо {format_rub(audit.offer_price)} по заявке №{audit.id}"

    def decline(self, audit: Expertise) -> str:
        """Заказчик отказался: заявка возвращается в общий список."""

        release(audit)

        return f"Заказчик отказался от цены по заявке №{audit.id}, заявка вернулась в общий список"


class AnswerCounterUseCase:
    """Руководитель группы соглашается на цену заказчика или отказывается от заявки."""

    def __init__(
        self, expertises: ExpertiseRepository, notifications: NotificationRepository
    ) -> None:
        self.expertises = expertises
        self.notifications = notifications

    async def execute(self, lead: User, audit: Expertise, accept: bool) -> Expertise:
        """Бросает ExpertiseAccessError и ExpertiseStateError."""

        if audit.expert_id != lead.id:
            raise ExpertiseAccessError("Ответить может только аудитор, предложивший цену")

        if audit.status != ExpertiseStatus.COUNTER or audit.counter_price is None:
            raise ExpertiseStateError("Встречного предложения сейчас нет")

        counter = audit.counter_price

        if accept:
            agree(audit, counter)
            text = (
                f"Аудитор НПИ «Недра» согласился на цену {format_rub(counter)} по заявке "
                f"№{audit.id}. Ознакомьтесь с договором и подпишите его"
            )
        else:
            release(audit)
            text = (
                f"Аудитор не согласился на цену по заявке №{audit.id}. Заявка вернулась "
                "в общий список, её может взять другой аудитор"
            )

        self.notifications.add_all([notify(audit.customer_id, audit, text)])

        return await self.expertises.save(audit)
