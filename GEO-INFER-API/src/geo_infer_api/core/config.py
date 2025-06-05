"""
Configuration settings for the GEO-INFER-API.
"""
import os
from functools import lru_cache
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, Field, validator


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application metadata
    app_name: str = "GEO-INFER-API"
    app_version: str = "0.1.0"
    
    # API settings
    api_prefix: str = "/api/v1"
    
    # CORS settings
    cors_origins: List[str] = ["*"]
    
    # Security settings
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database settings
    database_url: Optional[str] = Field(None, env="DATABASE_URL")
    
    # OGC API settings
    ogc_api_features_enabled: bool = True
    ogc_api_processes_enabled: bool = True
    
    @validator("cors_origins", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings to avoid reloading from env every time."""
    return Settings(
        # Default secret key for development only
        secret_key=os.getenv("SECRET_KEY", "dev_secret_key_change_in_production")
    ) 