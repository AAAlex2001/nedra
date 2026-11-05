"""Просмотр обращений."""

from src.requests.repositories.contact_requests import ContactRequestRepository
from src.requests.schemas.contact_request import ContactRequestResponse


class ListContactRequestsUseCase:
    """Список обращений для администратора."""

    def __init__(self, *, requests: ContactRequestRepository) -> None:
        """Репозиторий обращений."""

        self.requests = requests

    async def execute(self) -> list[ContactRequestResponse]:
        """Получить обращения."""

        contact_requests = await self.requests.list_all()

        return [
            ContactRequestResponse.from_model(contact_request=request)
            for request in contact_requests
        ]
