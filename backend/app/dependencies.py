from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.services.request import RequestService


def get_request_service(
    session: AsyncSession = Depends(get_session),
) -> RequestService:
    return RequestService(session)
