"""Просмотр заявок администратором."""

from src.expertise.admin.schemas.expertise import ExpertiseAdminResponse
from src.expertise.repositories.expertises import ExpertiseRepository
from src.users.exceptions import UserNotFoundError
from src.users.repositories.users import UserRepository


class ListAdminExpertisesUseCase:
    """Список работ с именами участников."""

    def __init__(
        self,
        *,
        expertises: ExpertiseRepository,
        users: UserRepository,
    ) -> None:
        """Работы и участники."""

        self.expertises = expertises
        self.users = users

    async def execute(self) -> list[ExpertiseAdminResponse]:
        """Получить все работы."""

        expertises = await self.expertises.list_all()
        user_ids = {record.customer_id for record in expertises}
        user_ids.update(record.expert_id for record in expertises if record.expert_id is not None)
        users = await self.users.list_by_ids(user_ids=user_ids)
        response = []

        for expertise in expertises:
            customer = users.get(expertise.customer_id)
            if customer is None:
                raise UserNotFoundError()

            expert = users.get(expertise.expert_id)
            response.append(
                ExpertiseAdminResponse(
                    id=expertise.id,
                    status=expertise.status,
                    customer_id=customer.id,
                    customer_name=customer.full_name,
                    expert_id=expertise.expert_id,
                    expert_name=expert.full_name if expert is not None else None,
                    object_name=expertise.object_name,
                    price=expertise.price,
                    created_at=expertise.created_at,
                ),
            )

        return response
