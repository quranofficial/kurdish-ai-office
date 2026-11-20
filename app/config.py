from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Kurdish AI Office"
    environment: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000"
    public_app_url: str = ""
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    telegram_bot_token: str = ""
    telegram_webhook_secret: str = ""
    office_admin_telegram_ids: str = ""
    office_api_key: str = ""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

    @property
    def office_admin_telegram_id_list(self) -> set[int]:
        values = {item.strip() for item in self.office_admin_telegram_ids.split(",") if item.strip()}
        return {int(item) for item in values if item.isdigit()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
