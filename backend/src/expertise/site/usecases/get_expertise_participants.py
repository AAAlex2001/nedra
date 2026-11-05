"""Просмотр участников экспертизы."""

from src.expertise.repositories.expertise_customers import ExpertiseCustomerRepository
from src.expertise.schemas.expertise_company import ExpertiseCompanyResponse
from src.expertise.schemas.expertise_participants import (
    ExpertiseParticipantResponse,
    ExpertiseParticipantsResponse,
)
from src.expertise.schemas.individual import IndividualResponse
from src.expertise.site.expertise_access import ExpertiseAccess
from src.users.exceptions import UserNotFoundError
from src.users.models.user import User
from src.users.repositories.users import UserRepository


class GetExpertiseParticipantsUseCase:
    """Участники и реквизиты заказчика."""

    def __init__(
        self,
        *,
        access: ExpertiseAccess,
        users: UserRepository,
        customers: ExpertiseCustomerRepository,
    ) -> None:
        """Права доступа, участники и реквизиты."""

        self.access = access
        self.users = users
        self.customers = customers

    async def execute(
        self,
        *,
        expertise_id: int,
        user: User,
    ) -> ExpertiseParticipantsResponse:
        """Получить участников экспертизы."""

        expertise = await self.access.get_visible(
            expertise_id=expertise_id,
            user=user,
        )
        customer = await self.users.get_by_id(user_id=expertise.customer_id)

        if customer is None:
            raise UserNotFoundError()

        expert_response = None

        if expertise.expert_id is not None:
            expert = await self.users.get_by_id(user_id=expertise.expert_id)

            if expert is None:
                raise UserNotFoundError()

            expert_response = ExpertiseParticipantResponse.from_model(user=expert)

        company = await self.customers.get_company(expertise_id=expertise_id)
        individual = await self.customers.get_individual(expertise_id=expertise_id)
        company_response = None
        individual_response = None

        if company is not None:
            company_response = ExpertiseCompanyResponse.from_model(company=company)

        if individual is not None:
            individual_response = IndividualResponse.from_model(individual=individual)

        return ExpertiseParticipantsResponse(
            customer=ExpertiseParticipantResponse.from_model(user=customer),
            expert=expert_response,
            customer_type=expertise.customer_type,
            company=company_response,
            individual=individual_response,
        )
