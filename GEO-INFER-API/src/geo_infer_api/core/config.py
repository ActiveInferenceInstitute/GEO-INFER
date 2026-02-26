"""
Configuration settings for the GEO-INFER-API.
"""
import os
from functools import lru_cache
from typing import List, Optional, Union

from pydantic import field_validator
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    _SETTINGS_CONFIG = SettingsConfigDict(env_file=".env", case_sensitive=True)
except ImportError:
    from pydantic import BaseSettings  # type: ignore[no-redef]
    _SETTINGS_CONFIG = None  # type: ignore[assignment]


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    if _SETTINGS_CONFIG is not None:
        model_config = _SETTINGS_CONFIG

    # Application metadata
    app_name: str = "GEO-INFER-API"
    app_version: str = "0.2.0"

    # API settings
    api_prefix: str = "/api/v1"

    # CORS settings
    cors_origins: List[str] = ["*"]

    # Security settings
    secret_key: str = "dev_secret_key_change_in_production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Database settings
    database_url: Optional[str] = None

    # OGC API settings
    ogc_api_features_enabled: bool = True
    ogc_api_processes_enabled: bool = True

    @field_validator("cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v  # type: ignore[return-value]
        raise ValueError(v)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings to avoid reloading from env every time."""
    secret = os.getenv("SECRET_KEY", "dev_secret_key_change_in_production")
    return Settings(secret_key=secret)
