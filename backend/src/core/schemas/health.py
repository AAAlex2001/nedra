"""Доступность приложения."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Состояние HTTP API."""

    status: str = "ok"
