"""Модуль конфигурации API."""

import os
from os.path import abspath, dirname
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["api_settings"]

ENV_DIR = os.path.join(dirname(abspath(__file__)), ".env")


class Settings(BaseSettings):
    """Класс для доступа к переменным окружения."""

    MODE: Literal["DEV", "TEST", "LOCAL"]
    APP_NAME: str = "Todo List API"
    APP_VERSION: str = "0.1.0"

    # Postgres
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POOL_SIZE: int
    MAX_OVERFLOW: int

    @property
    def DATABASE_URL(self):
        """URL базы данных."""

        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(env_file=ENV_DIR, extra="allow")


api_settings: Settings = Settings()
