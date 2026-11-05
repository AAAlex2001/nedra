"""Просмотр зарегистрированных заказчиков."""

from src.users.admin.schemas.customer import CustomerResponse
from src.users.enums import UserRole
from src.users.repositories.customer_activity import CustomerActivityRepository
from src.users.repositories.users import UserRepository


class ListCustomersUseCase:
    """Заказчики со сводкой заявок."""

    def __init__(
        self,
        *,
        users: UserRepository,
        activity: CustomerActivityRepository,
    ) -> None:
        """Аккаунты и заявки заказчиков."""

        self.users = users
        self.activity = activity

    async def execute(self) -> list[CustomerResponse]:
        """Получить заказчиков."""

        users = await self.users.list_by_role(role=UserRole.CUSTOMER)
        counts_by_customer = await self.activity.count_by_customers()
        companies_by_customer = await self.activity.get_latest_companies()

        customers = []

        for user in users:
            customer = CustomerResponse.from_model(
                user=user,
                company=companies_by_customer.get(user.id),
                requests_count=counts_by_customer.get(user.id, 0),
            )
            customers.append(customer)

        return customers
