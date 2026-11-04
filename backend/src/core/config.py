"""Конфигурация приложения через переменные окружения."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения, читаемые из окружения и файла .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = Field(..., description="URL подключения к PostgreSQL")
    cors_origins: list[str] = Field(default_factory=list)
    debug: bool = False

    smtp_host: str = ""
    smtp_port: int = 465
    smtp_user: str = ""
    smtp_password: str = ""
    notify_emails: list[str] = Field(default_factory=list)

    admin_api_token: str = ""
    media_dir: str = "media"
    private_dir: str = "private"
    cookie_secure: bool = True

    jwt_secret: str = Field(..., min_length=32)
    jwt_expires_days: int = 7

    yookassa_shop_id: str = ""
    yookassa_secret_key: str = ""
    payment_return_url: str = ""

    company_name: str = 'ООО "НПИ «Недра»"'
    company_inn: str = ""
    company_kpp: str = ""
    company_address: str = ""
    company_bank: str = ""
    company_bik: str = ""
    company_account: str = ""
    company_corr_account: str = ""
    company_director: str = ""
    company_vat_rate: int = 0
    pdf_font_path: str = ""

    @property
    def yookassa_vat_code(self) -> int:
        """Код ставки НДС для чека ЮKassa."""

        mapping = {0: 1, 5: 7, 7: 8, 10: 3, 20: 4}
        return mapping.get(self.company_vat_rate, 1)


@lru_cache
def get_settings() -> Settings:
    """Возвращает кэшированный экземпляр настроек."""

    return Settings()
