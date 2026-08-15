import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str = "MOCK_BOT_TOKEN"
    DATABASE_URL: str = "sqlite+aiosqlite:///car_auction.db"
    ADMIN_IDS: list[int] = [123456789]
    DEFAULT_LOGISTICS_BASE_USD: float = 1800.0  # Base US -> Poti -> Yerevan transport
    DEFAULT_BROKER_FEE_USD: float = 300.0       # Broker processing fee

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
