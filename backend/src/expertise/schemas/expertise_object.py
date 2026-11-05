"""Объект экспертизы."""

from pydantic import BaseModel

from src.expertise.models.expertise import Expertise


class ExpertiseObjectResponse(BaseModel):
    """Объект и требования к эксперту."""

    name: str | None  # Наименование документации.
    object_code: str | None  # Код объекта экспертизы.
    area_code: str | None  # Область аттестации.
    hazard_class: int | None  # Класс опасности ОПО.
    expert_category: int | None  # Требуемая категория эксперта.

    @classmethod
    def from_model(cls, *, expertise: Expertise) -> "ExpertiseObjectResponse":
        """Объект экспертизы."""

        return cls(
            name=expertise.object_name,
            object_code=expertise.object_code,
            area_code=expertise.area_code,
            hazard_class=expertise.hazard_class,
            expert_category=expertise.expert_category,
        )
