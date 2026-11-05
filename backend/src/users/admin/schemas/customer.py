"""Заказчик в административной части."""

from datetime import datetime

from pydantic import BaseModel, EmailStr

from src.users.customer_company import CustomerCompany
from src.users.models.user import User


class CustomerResponse(BaseModel):
    """Контакты и сведения о заявках."""

    user_id: int
    email: EmailStr
    full_name: str
    phone: str
    created_at: datetime
    company_name: str | None
    company_inn: str | None
    expertises_count: int

    @classmethod
    def from_model(
        cls,
        *,
        user: User,
        company: CustomerCompany | None,
        requests_count: int,
    ) -> "CustomerResponse":
        """Подготовить данные заказчика."""

        return cls(
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            created_at=user.created_at,
            company_name=company.name if company is not None else None,
            company_inn=company.inn if company is not None else None,
            expertises_count=requests_count,
        )
