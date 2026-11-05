"""Правила контактов, аттестации и выбора экспертизы."""

import pytest

from src.auth.exceptions import WeakPasswordError
from src.auth.passwords import validate_password
from src.contracts.enums import ContractKind
from src.expertise.application_validation import (
    determine_contract_kind,
    determine_expert_category,
    validate_expertise_codes,
)
from src.expertise.exceptions import InvalidExpertiseError
from src.users.attestation_validation import validate_certificate, validate_directions
from src.users.contact_validation import normalize_phone
from src.users.exceptions import InvalidCertificateError, InvalidDirectionError, InvalidPhoneError


def test_password_requires_letter_digit_and_sufficient_length() -> None:
    validate_password(password="abc12345")

    for password in ("12345678", "abcdefgh", "short1"):
        with pytest.raises(WeakPasswordError):
            validate_password(password=password)


def test_phone_normalization() -> None:
    assert normalize_phone(phone="8 999 000 00 00") == "89990000000"
    assert normalize_phone(phone="+7 999 000-00-00") == "+79990000000"

    with pytest.raises(InvalidPhoneError):
        normalize_phone(phone="12345")


def test_certificate_combinations() -> None:
    for area_code, object_code, category in (("Э4", "kl", 1), ("Э1", "kl_tp", 3), ("Э2", "d", 2)):
        validate_certificate(area_code=area_code, object_code=object_code, category=category)

    for area_code, object_code in (("Э1", "d"), ("Э1", "tp"), ("Э4", "kl_tp"), ("Э4", "tu")):
        with pytest.raises(InvalidCertificateError):
            validate_certificate(area_code=area_code, object_code=object_code, category=1)


def test_directions_are_known_and_unique() -> None:
    validate_directions(directions=["ecology", "design"])

    for directions in ([], ["ecology", "ecology"], ["unknown"]):
        with pytest.raises(InvalidDirectionError):
            validate_directions(directions=directions)


@pytest.mark.parametrize(
    ("hazard_class", "requested_category", "expected_category"),
    [(1, None, 1), (2, None, 2), (4, None, 3), (4, 1, 3), (None, 2, 2), (None, None, None)],
)
def test_category_follows_hazard_class(
    hazard_class: int | None,
    requested_category: int | None,
    expected_category: int | None,
) -> None:
    assert (
        determine_expert_category(
            hazard_class=hazard_class,
            expert_category=requested_category,
        )
        == expected_category
    )


def test_expertise_object_belongs_to_area() -> None:
    validate_expertise_codes(object_code="kl_tp", area_code="Э1")
    validate_expertise_codes(object_code="kl", area_code="Э4")

    for object_code in ("kl", "d"):
        with pytest.raises(InvalidExpertiseError):
            validate_expertise_codes(object_code=object_code, area_code="Э1")


@pytest.mark.parametrize(
    ("object_code", "chosen_kind", "expected_kind"),
    [
        ("tp", None, ContractKind.REEQUIPMENT),
        ("d", None, ContractKind.DECLARATION),
        ("ob", None, ContractKind.JUSTIFICATION),
        ("kl", None, None),
        (None, None, None),
        ("kl", ContractKind.LIQUIDATION, ContractKind.LIQUIDATION),
        ("kl_tp", ContractKind.REEQUIPMENT, ContractKind.REEQUIPMENT),
        (None, ContractKind.DECLARATION, ContractKind.DECLARATION),
    ],
)
def test_contract_matches_object(
    object_code: str | None,
    chosen_kind: ContractKind | None,
    expected_kind: ContractKind | None,
) -> None:
    assert (
        determine_contract_kind(object_code=object_code, chosen_kind=chosen_kind) == expected_kind
    )


def test_incompatible_contract_is_rejected() -> None:
    with pytest.raises(InvalidExpertiseError):
        determine_contract_kind(object_code="kl", chosen_kind=ContractKind.REEQUIPMENT)
