"""Сценарий удаления заявки."""

from src.requests.exceptions import RequestNotFoundError
from src.requests.repositories.requests import RequestRepository


class DeleteRequestUseCase:
    """Удаляет заявку по идентификатору."""

    def __init__(self, *, requests: RequestRepository) -> None:
        """Принимает репозиторий заявок."""

        self.requests = requests

    async def execute(self, *, request_id: int) -> None:
        """Удаляет заявку или выбрасывает ошибку, если она не найдена."""

        request = await self.requests.get_by_id(request_id=request_id)
        if request is None:
            raise RequestNotFoundError("Заявка не найдена.")
        await self.requests.delete(request=request)
