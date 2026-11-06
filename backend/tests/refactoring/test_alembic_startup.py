"""Запуск миграций с новым приложением."""

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine

from src.core.models import Base


async def test_alembic_upgrades_empty_database(
    database_engine: AsyncEngine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Пройти всю цепочку через действующее окружение Alembic."""

    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://unused:unused@localhost/unused")
    monkeypatch.setenv("JWT_SECRET", "migration-test-secret-at-least-32-characters")
    backend = Path(__file__).resolve().parents[2]

    def migrate(connection: Connection) -> None:
        config = Config(str(backend / "alembic.ini"))
        config.set_main_option("script_location", str(backend / "alembic"))
        config.attributes["connection"] = connection
        command.upgrade(config, "head")
        assert connection.scalar(text("SELECT version_num FROM alembic_version")) == "0029"
        assert set(Base.metadata.tables).issubset(inspect(connection).get_table_names())

    async with database_engine.begin() as connection:
        await connection.run_sync(migrate)
