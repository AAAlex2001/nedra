"""Сценарий создания заявки с сайта."""

from app.models.request import Request
from app.schemas.request import RequestInSchema
from app.services.requests.catalog import ACTIVITY_DIRECTION
from app.services.requests.exceptions import UnknownActivityError
from app.services.requests.repo import RequestRepository


class CreateRequestUseCase:
    """Определить направление по услуге и сохранить заявку."""

    def __init__(self, requests: RequestRepository) -> None:
        self.requests = requests

    async def execute(self, data: RequestInSchema) -> Request:
        """Создать заявку. Бросает UnknownActivityError."""

        direction = ACTIVITY_DIRECTION.get(data.activity)
        if direction is None:
            raise UnknownActivityError(
                f"Недопустимое значение вида деятельности: {data.activity}"
            )

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

        return await self.requests.add(request)
