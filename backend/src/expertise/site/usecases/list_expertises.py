"""Списки экспертиз в кабинете."""

from typing import Literal

from src.expertise.exceptions import ExpertiseAccessError
from src.expertise.repositories.expertises import ExpertiseRepository
from src.expertise.site.schemas.list_expertises import ExpertiseListItemResponse
from src.users.enums import UserRole
from src.users.models.user import User


class ListExpertisesUseCase:
    """Свои, назначенные и доступные работы."""

    def __init__(self, *, expertises: ExpertiseRepository) -> None:
        """Работы пользователя."""

        self.expertises = expertises

    async def execute(
        self,
        *,
        user: User,
        scope: Literal["my", "assigned", "incoming"],
        object_code: str | None = None,
        area_code: str | None = None,
    ) -> list[ExpertiseListItemResponse]:
        """Получить выбранный список работ."""

        if scope == "my":
            if user.role != UserRole.CUSTOMER:
                raise ExpertiseAccessError("Этот список доступен заказчику")

            expertises = await self.expertises.list_for_customer(user_id=user.id)
        else:
            if user.role != UserRole.EXPERT:
                raise ExpertiseAccessError("Этот список доступен эксперту")

            if scope == "assigned":
                expertises = await self.expertises.list_assigned(user_id=user.id)
            else:
                expertises = await self.expertises.list_incoming(
                    user_id=user.id,
                    object_code=object_code,
                    area_code=area_code,
                )

        return [
            ExpertiseListItemResponse.from_model(expertise=expertise) for expertise in expertises
        ]
