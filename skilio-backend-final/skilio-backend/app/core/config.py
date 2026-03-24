"""
app/core/config.py
──────────────────
Pydantic BaseSettings — reads from .env file if present, otherwise uses defaults.

The app works with ZERO configuration:
  - SQLite is the default database (no MySQL, no .env needed)
  - A safe dev SECRET_KEY is built in (change before any real deployment)

To switch databases, set DATABASE_URL in .env:
  SQLite (default):   sqlite:///./skilio.db
  MySQL  (+5 marks):  mysql+pymysql://user:pass@localhost:3306/skilio_db
  PostgreSQL:         postgresql://user:pass@localhost:5432/skilio_db
"""
from functools import lru_cache
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "Skilio"
    app_version: str = "1.0.0"
    debug: bool = False

    # ── Database — SQLite by default, zero config ─────────────────────────────
    database_url: str = "sqlite:///./skilio.db"

    # ── Security ──────────────────────────────────────────────────────────────
    # Dev-safe default (32+ chars). MUST change before any real deployment.
    secret_key: str = "skilio-dev-secret-key-change-before-production-deploy-now"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # ── CORS ──────────────────────────────────────────────────────────────────
    allowed_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # ── Rate limiting ─────────────────────────────────────────────────────────
    login_rate_limit_per_minute: int = 10
    register_rate_limit_per_minute: int = 5

    # ── Request size limits ───────────────────────────────────────────────────
    max_request_body_bytes: int = 1_048_576  # 1 MB

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, str):
            return [o.strip() for o in v.split(",")]
        return v

    @field_validator("secret_key")
    @classmethod
    def check_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    @property
    def is_mysql(self) -> bool:
        return "mysql" in self.database_url.lower()


@lru_cache
def get_settings() -> Settings:
    return Settings()
