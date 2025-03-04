# src/stockalpha/utils/config.py
import os
from functools import lru_cache
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    """Application settings"""

    # API settings
    api_title: str = "Stock Alpha API"
    api_description: str = "API for Stock Alpha Platform"
    api_v1_prefix: str = "/api/v1"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Database settings
    database_url: PostgresDsn
    db_echo: bool = False

    # Additional config from YAML (if needed)
    yaml_config: Dict[str, Any] = {}

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached)"""
    return Settings()


settings = get_settings()
