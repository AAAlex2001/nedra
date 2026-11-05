"""Подача обращения."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.requests.exceptions import UnknownActivityError
from src.requests.models.contact_request import ContactRequest
from src.requests.options import ACTIVITY_DIRECTION
from src.requests.repositories.contact_requests import ContactRequestRepository
from src.requests.schemas.contact_request import (
    ContactRequestResponse,
    CreateContactRequest,
)
from src.requests.site.contact_request_letters import ContactRequestLetters


class CreateContactRequestUseCase:
    """Сохранение обращения с сайта."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        requests: ContactRequestRepository,
        letters: ContactRequestLetters,
    ) -> None:
        """Зависимости подачи обращения."""

        self.session = session
        self.requests = requests
        self.letters = letters

    async def execute(self, *, payload: CreateContactRequest) -> ContactRequestResponse:
        """Подать обращение."""

        direction = ACTIVITY_DIRECTION.get(payload.activity)

        if direction is None:
            raise UnknownActivityError("Неизвестная услуга")

        contact_request = ContactRequest(
            name=payload.name,
            telephone=payload.telephone,
            email=str(payload.email),
            activity=payload.activity,
            direction=direction,
            company_name=payload.company_name,
            inn=payload.inn,
            comment=payload.comment,
        )
        await self.requests.add(contact_request=contact_request)
        response = ContactRequestResponse.from_model(contact_request=contact_request)
        await self.session.commit()
        await self.letters.send_created(contact_request=contact_request)

        return response
