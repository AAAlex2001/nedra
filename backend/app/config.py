from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

VAT_CODES = {0: 1, 5: 7, 7: 8, 10: 3, 20: 4}


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
    pdf_font_path: str | None = None

    @property
    def yookassa_vat_code(self) -> int:
        """Код ставки НДС для чека ЮKassa. Неизвестная ставка — как без НДС."""

        return VAT_CODES.get(self.company_vat_rate, 1)


@lru_cache
def get_settings() -> Settings:
    return Settings()
