"""Application configuration — loaded from environment variables."""

from __future__ import annotations

import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """App settings pulled from env vars / .env.local file."""

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # Anthropic
    anthropic_api_key: str = ""

    # Redis (blank = use in-memory fallback)
    redis_url: str = ""

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # Scoring
    score_min: int = 0
    score_max: int = 1000

    model_config = {
        "env_file": ".env.local",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache()
def get_settings() -> Settings:
    """Singleton settings — cached after first call."""
    return Settings()
