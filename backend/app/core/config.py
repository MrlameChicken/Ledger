from functools import lru_cache
from typing import List

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    app_name: str = Field("Ledger API", env="LEDGER_APP_NAME")
    api_v1_prefix: str = "/api/v1"
    secret_key: str = Field("change-me", env="LEDGER_SECRET_KEY")
    access_token_expire_minutes: int = Field(30, env="LEDGER_ACCESS_TOKEN_EXPIRE")
    refresh_token_expire_minutes: int = Field(60 * 24 * 7, env="LEDGER_REFRESH_TOKEN_EXPIRE")

    database_url: str = Field(
        "sqlite:///./ledger.db",
        env="LEDGER_DATABASE_URL",
    )
    alembic_database_url: str | None = Field(None, env="LEDGER_ALEMBIC_DATABASE_URL")

    cors_origins: List[str] = Field(default_factory=lambda: ["*"])

    @validator("cors_origins", pre=True)
    def split_origins(cls, value: str | List[str]) -> List[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
