from sqlalchemy.ext.asyncio import AsyncSession

from app.models.request import Request
from app.schemas.request import RequestInSchema
from app.services.requestDTO import ACTIVITY_DIRECTION


class RequestService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db


    @staticmethod
    def map_activity_to_direction(activity: int) -> int:
        direction = ACTIVITY_DIRECTION.get(activity)
        if direction is None:
            raise ValueError(f"Недопустимое значение вида деятельности: {activity}")
        return direction


    async def create_request(self, request_data: RequestInSchema) -> Request:
        """Создание заявки."""

        request = Request(
            name=request_data.name,
            telephone=request_data.telephone,
            email=request_data.email,
            activity=request_data.activity,
            direction=self.map_activity_to_direction(request_data.activity),
            company_name=request_data.company_name,
            inn=request_data.inn,
            comment=request_data.comment
        )

        self.db.add(request)
        await self.db.commit()
        await self.db.refresh(request)
        return request