"""Удостоверения одобренного эксперта: добавить, изменить, удалить.

Сценарии общие для админки и личного кабинета: эксперт сам дополняет
удостоверения, если забыл указать их в заявке, а админ правит любые.
"""

from app.models.expert import ExpertCertificate
from app.schemas.expert import CertificateInSchema
from app.services.experts.catalog import OBJECT_BY_CODE
from app.services.experts.exceptions import CertificateNotFoundError, InvalidCertificateError
from app.services.experts.repo import ExpertProfileRepository
from app.services.experts.validators import validate_certificate


def check_certificate(
    data: CertificateInSchema, existing: list[ExpertCertificate], skip_id: int | None = None
) -> str:
    """Проверить удостоверение по справочнику и на повтор. Вернуть номер без пробелов по краям.

    Бросает InvalidCertificateError.
    """

    validate_certificate(data.area_code, data.object_code, data.category)

    number = data.number.strip()
    if not number:
        raise InvalidCertificateError("Укажите номер удостоверения или регистрации в ЕРУЛ")

    for item in existing:
        same_pair = item.area_code == data.area_code and item.object_code == data.object_code
        if same_pair and item.id != skip_id:
            label = OBJECT_BY_CODE[data.object_code].label
            raise InvalidCertificateError(
                f"Удостоверение {data.area_code} · {label} уже есть — измените его"
            )

    return number


class AddCertificateUseCase:
    """Добавить эксперту ещё одно удостоверение."""

    def __init__(self, profiles: ExpertProfileRepository) -> None:
        self.profiles = profiles

    async def execute(self, user_id: int, data: CertificateInSchema) -> ExpertCertificate:
        """Бросает InvalidCertificateError."""

        existing = await self.profiles.list_certificates(user_id)
        number = check_certificate(data, existing)

        certificate = ExpertCertificate(
            user_id=user_id,
            area_code=data.area_code,
            object_code=data.object_code,
            category=data.category,
            valid_until=data.valid_until,
            number=number,
        )

        return await self.profiles.add_certificate(certificate)


class UpdateCertificateUseCase:
    """Поменять область, объект, категорию, срок или номер удостоверения."""

    def __init__(self, profiles: ExpertProfileRepository) -> None:
        self.profiles = profiles

    async def execute(
        self, user_id: int, certificate_id: int, data: CertificateInSchema
    ) -> ExpertCertificate:
        """Бросает CertificateNotFoundError и InvalidCertificateError."""

        certificate = await self.profiles.get_certificate(user_id, certificate_id)
        if certificate is None:
            raise CertificateNotFoundError(f"Удостоверение {certificate_id} не найдено")

        existing = await self.profiles.list_certificates(user_id)
        number = check_certificate(data, existing, skip_id=certificate.id)

        certificate.area_code = data.area_code
        certificate.object_code = data.object_code
        certificate.category = data.category
        certificate.valid_until = data.valid_until
        certificate.number = number

        await self.profiles.save()

        return certificate


class DeleteCertificateUseCase:
    """Убрать удостоверение. Последнее удалить нельзя: без него эксперт не видит заявок."""

    def __init__(self, profiles: ExpertProfileRepository) -> None:
        self.profiles = profiles

    async def execute(self, user_id: int, certificate_id: int) -> ExpertCertificate:
        """Бросает CertificateNotFoundError и InvalidCertificateError."""

        certificate = await self.profiles.get_certificate(user_id, certificate_id)
        if certificate is None:
            raise CertificateNotFoundError(f"Удостоверение {certificate_id} не найдено")

        existing = await self.profiles.list_certificates(user_id)
        if len(existing) <= 1:
            raise InvalidCertificateError("Должно остаться хотя бы одно удостоверение")

        await self.profiles.remove_certificate(certificate)

        return certificate
