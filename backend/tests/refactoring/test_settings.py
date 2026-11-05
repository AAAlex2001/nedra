"""Загрузка настроек окружения."""

import pytest

from src.core.settings import Settings


def test_empty_optional_environment_settings_use_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    """Оставить необязательные пустые настройки незаданными."""

    monkeypatch.setenv("PDF_FONT_PATH", "")
    monkeypatch.setenv("SMTP_HOST", "")
    monkeypatch.setenv("PAYMENT_RETURN_URL", "")
    settings = Settings(
        _env_file=None,
        database_url="postgresql+asyncpg://unused@localhost/unused",
        jwt_secret="test-settings-secret-at-least-32-characters",
    )

    assert settings.pdf_font_path is None
    assert settings.smtp_host is None
    assert settings.payment_return_url is None
