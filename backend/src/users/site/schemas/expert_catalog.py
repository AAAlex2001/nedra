"""Справочник регистрации эксперта."""

from pydantic import BaseModel

from src.users.catalog_items import AttestationArea, Direction, ExpertiseObject


class HazardClassResponse(BaseModel):
    """Категория эксперта для класса опасности."""

    hazard_class: int
    category: int


class ExpertCatalogResponse(BaseModel):
    """Направления и области аттестации."""

    directions: list[Direction]
    areas: list[AttestationArea]
    objects: list[ExpertiseObject]
    categories: list[int]
    hazard_classes: list[HazardClassResponse]
