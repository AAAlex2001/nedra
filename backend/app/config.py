from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    cors_origins: list[str] = []
    debug: bool = False

    smtp_host: str | None = None
    smtp_port: int = 465
    smtp_user: str | None = None
    smtp_password: str | None = None
    notify_emails: list[str] = []

    admin_api_token: str | None = None
    media_dir: str = "media"
    private_dir: str = "private"
    cookie_secure: bool = True

    jwt_secret: str = Field(min_length=32)
    jwt_expires_days: int = 7

    yookassa_shop_id: str | None = None
    yookassa_secret_key: str | None = None
    payment_return_url: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
