"""Сценарий создания заявки с сайта."""

from src.requests.catalog import ACTIVITY_DIRECTION
from src.requests.exceptions import UnknownActivityError
from src.requests.models import Request
from src.requests.repositories.requests import RequestRepository
from src.requests.schemas import RequestInSchema


class CreateRequestUseCase:
    """Создаёт заявку на основе входных данных."""

    def __init__(self, *, requests: RequestRepository) -> None:
        """Принимает репозиторий заявок."""

        self.requests = requests

    async def execute(self, *, data: RequestInSchema) -> Request:
        """Создаёт заявку и возвращает сохранённую сущность."""

        direction = ACTIVITY_DIRECTION.get(data.activity)
        if direction is None:
            raise UnknownActivityError("Неизвестный вид деятельности.")

        request = Request(
            name=data.name,
            telephone=data.telephone,
            email=data.email,
            activity=data.activity,
            direction=direction,
            company_name=data.company_name,
            inn=data.inn,
            comment=data.comment,
        )
        return await self.requests.add(request=request)
