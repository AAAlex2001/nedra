"""Настройки окружения."""

from pathlib import Path

from fastapi import Request
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.options import BACKEND_DIRECTORY, ENV_FILE


class Settings(BaseSettings):
    """Настройки приложения."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_ignore_empty=True,
        extra="ignore",
    )

    database_url: str = Field(repr=False)
    jwt_secret: str = Field(
        min_length=32,
        repr=False,
    )
    jwt_expires_days: int = Field(
        default=7,
        gt=0,
    )
    cookie_secure: bool = True
    cors_origins: list[str] = Field(default_factory=list)
    debug: bool = False
    admin_api_token: str | None = Field(
        default=None,
        repr=False,
    )
    site_url: str = "https://nedra-npi.ru"

    smtp_host: str | None = None
    smtp_port: int = Field(
        default=465,
        ge=1,
        le=65535,
    )
    smtp_user: str | None = None
    smtp_password: str | None = Field(
        default=None,
        repr=False,
    )
    notify_emails: list[str] = Field(default_factory=list)

    media_dir: Path = BACKEND_DIRECTORY / "media"
    private_dir: Path = BACKEND_DIRECTORY / "private"
    pdf_font_path: Path | None = None

    yookassa_shop_id: str | None = None
    yookassa_vat_code: int = Field(
        default=1,
        ge=1,
    )
    yookassa_secret_key: str | None = Field(
        default=None,
        repr=False,
    )
    payment_return_url: str | None = None

    company_name: str = "ООО «НПИ «Недра»"
    company_inn: str | None = None
    company_kpp: str | None = None
    company_address: str | None = None
    company_bank: str | None = None
    company_bic: str | None = None
    company_account: str | None = None
    company_corr_account: str | None = None
    company_director: str | None = None
    company_vat_rate: int = 0

    @field_validator(
        "media_dir",
        "private_dir",
        "pdf_font_path",
    )
    @classmethod
    def resolve_path(cls, configured_path: Path | None) -> Path | None:
        """Разрешить путь относительно backend."""

        if configured_path is None or configured_path.is_absolute():
            return configured_path

        return (BACKEND_DIRECTORY / configured_path).resolve()

    @property
    def cabinet_url(self) -> str:
        """Адрес личного кабинета."""

        return f"{self.site_url.rstrip('/')}/kabinet"


def get_settings(*, request: Request) -> Settings:
    """Настройки запущенного приложения."""

    return request.app.state.settings
