# src/stockalpha/utils/config.py
import os
from functools import lru_cache
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    """Application settings"""

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
