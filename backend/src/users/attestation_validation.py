"""Проверка аттестации по справочнику."""

from src.users.exceptions import InvalidCertificateError, InvalidDirectionError
from src.users.models.expert_certificate import ExpertCertificate
from src.users.options import AREA_BY_CODE, CATEGORIES, DIRECTION_CODES


def validate_directions(*, directions: list[str]) -> None:
    """Проверить направления работы."""

    if not directions:
        raise InvalidDirectionError("Выберите направления работы")

    if len(directions) != len(set(directions)):
        raise InvalidDirectionError("Направления повторяются")

    for direction in directions:
        if direction not in DIRECTION_CODES:
            raise InvalidDirectionError(f"Неизвестное направление: {direction}")


def validate_certificate(
    *,
    area_code: str,
    object_code: str,
    category: int,
) -> None:
    """Проверить область, объект и категорию."""

    area = AREA_BY_CODE.get(area_code)

    if area is None:
        raise InvalidCertificateError(f"Неизвестная область аттестации: {area_code}")

    if object_code not in area.objects:
        raise InvalidCertificateError("Указанный объект не входит в область аттестации")

    if category not in CATEGORIES:
        raise InvalidCertificateError("Категория должна быть от 1 до 3")


def validate_certificate_unique(
    *,
    area_code: str,
    object_code: str,
    certificates: list[ExpertCertificate],
    exclude_id: int | None = None,
) -> None:
    """Проверить, что такое удостоверение ещё не добавлено."""

    for certificate in certificates:
        if certificate.id == exclude_id:
            continue

        if certificate.area_code == area_code and certificate.object_code == object_code:
            raise InvalidCertificateError(
                "Удостоверение по этой области и объекту уже есть — измените его"
            )
