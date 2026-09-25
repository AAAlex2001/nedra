"""Шаг 2–3: эксперт посмотрел документацию и готов провести экспертизу."""

from datetime import datetime, timezone

from app.models.expertise import Expertise, ExpertiseStatus
from app.models.notification import Notification
from app.models.user import User
from app.services.contracts.kinds import resolve_kind
from app.services.experts.repo import ExpertProfileRepository
from app.services.expertise.exceptions import (
    ExpertiseAccessError,
    ExpertiseStateError,
    InvalidExpertiseError,
    PriceMissingError,
)
from app.services.expertise.repo import ExpertiseRepository, certificate_fits
from app.services.notifications.repo import NotificationRepository


class AcceptExpertiseUseCase:
    """Закрепить заявку за первым экспертом, который нажал «готов провести».

    У остальных экспертов заявка пропадает из входящих: expert_id заполнен.
    Без тарифа заявку взять нельзя, иначе на шаге договора нечего оплачивать.
    Если заказчик не знал вид проекта, вид договора определяет эксперт: у него
    право первой подписи, а заказчику остаётся согласиться с одним вариантом.
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

    async def execute(
        self, expert: User, expertise: Expertise, contract_kind: str | None = None
    ) -> Expertise:
        """Перевести заявку в expert_ready.

        Бросает ExpertiseStateError, ExpertiseAccessError, PriceMissingError, InvalidExpertiseError.
        """

        if expertise.status != ExpertiseStatus.NEW or expertise.expert_id is not None:
            raise ExpertiseStateError("Заявку уже взял другой эксперт")

        certificates = await self.profiles.list_certificates(expert.id)
        if not certificate_fits(certificates, expertise):
            raise ExpertiseAccessError("Ваша аттестация не подходит под эту заявку")

        if expertise.price is None:
            raise PriceMissingError("Для этой области и объекта не задан тариф")

        if expertise.contract_kind is None:
            expertise.contract_kind = resolve_kind(expertise.object_code, contract_kind)

        if expertise.contract_kind is None:
            raise InvalidExpertiseError("Выберите вид договора по проекту заказчика")

        expertise.expert_id = expert.id
        expertise.expert_ready_at = datetime.now(timezone.utc)
        expertise.status = ExpertiseStatus.EXPERT_READY

        self.notifications.add_all(
            [
                Notification(
                    user_id=expertise.customer_id,
                    expertise_id=expertise.id,
                    text=f"Эксперт {expert.full_name} готов провести экспертизу по заявке №{expertise.id}",
                )
            ]
        )

        return await self.expertises.save(expertise)
