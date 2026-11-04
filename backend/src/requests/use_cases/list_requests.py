"""Сценарий получения списка заявок."""

from src.requests.models import Request
from src.requests.repositories.requests import RequestRepository


class ListRequestsUseCase:
    """Возвращает все заявки, новые первыми."""

    def __init__(self, *, requests: RequestRepository) -> None:
        """Принимает репозиторий заявок."""

        self.requests = requests

    async def execute(self) -> list[Request]:
        """Возвращает список заявок."""

        return await self.requests.list_all()
