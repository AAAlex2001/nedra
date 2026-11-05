"""Сохранение удостоверений эксперта."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models.expert_certificate import ExpertCertificate


class ExpertCertificateRepository:
    """Удостоверения заявителей и экспертов."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def list_for_application(self, *, application_id: int) -> list[ExpertCertificate]:
        """Получить удостоверения заявки."""

        statement = (
            select(ExpertCertificate)
            .where(ExpertCertificate.application_id == application_id)
            .order_by(ExpertCertificate.id)
        )
        query_result = await self.session.scalars(statement)

        return list(query_result)

    async def list_for_user(self, *, user_id: int) -> list[ExpertCertificate]:
        """Получить удостоверения эксперта."""

        statement = (
            select(ExpertCertificate)
            .where(ExpertCertificate.user_id == user_id)
            .order_by(ExpertCertificate.id)
        )
        query_result = await self.session.scalars(statement)

        return list(query_result)

    async def get_for_user(
        self,
        *,
        user_id: int,
        certificate_id: int,
    ) -> ExpertCertificate | None:
        """Найти удостоверение выбранного эксперта."""

        statement = select(ExpertCertificate).where(
            ExpertCertificate.id == certificate_id,
            ExpertCertificate.user_id == user_id,
        )
        query_result = await self.session.scalars(statement)

        return query_result.one_or_none()

    async def save(self, *, certificate: ExpertCertificate) -> None:
        """Сохранить удостоверение."""

        self.session.add(certificate)
        await self.session.flush()

    async def remove(self, *, certificate: ExpertCertificate) -> None:
        """Удалить удостоверение."""

        await self.session.delete(certificate)
        await self.session.flush()

    async def add_many(self, *, certificates: list[ExpertCertificate]) -> None:
        """Добавить удостоверения."""

        self.session.add_all(certificates)
        await self.session.flush()

    async def list_for_users(self, *, user_ids: set[int]) -> dict[int, list[ExpertCertificate]]:
        """Сгруппировать удостоверения по экспертам."""

        if not user_ids:
            return {}

        statement = (
            select(ExpertCertificate)
            .where(ExpertCertificate.user_id.in_(user_ids))
            .order_by(ExpertCertificate.id)
        )
        query_result = await self.session.scalars(statement)
        certificates_by_user: dict[int, list[ExpertCertificate]] = {}

        for certificate in query_result:
            certificates_by_user.setdefault(certificate.user_id, []).append(certificate)

        return certificates_by_user

    async def get_for_application(
        self,
        *,
        application_id: int,
        certificate_id: int,
    ) -> ExpertCertificate | None:
        """Найти удостоверение из заявки."""

        statement = select(ExpertCertificate).where(
            ExpertCertificate.application_id == application_id,
            ExpertCertificate.id == certificate_id,
        )

        return await self.session.scalar(statement)

    async def list_for_applications(
        self, *, application_ids: set[int]
    ) -> dict[int, list[ExpertCertificate]]:
        """Сгруппировать удостоверения по заявкам."""

        if not application_ids:
            return {}

        statement = (
            select(ExpertCertificate)
            .where(ExpertCertificate.application_id.in_(application_ids))
            .order_by(ExpertCertificate.id)
        )
        query_result = await self.session.scalars(statement)
        certificates_by_application: dict[int, list[ExpertCertificate]] = {}

        for certificate in query_result:
            certificates_by_application.setdefault(certificate.application_id, []).append(
                certificate
            )

        return certificates_by_application
