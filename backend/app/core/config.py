"""
Application configuration.

All settings are loaded from environment variables (see .env.example).
Never hardcode secrets here.
"""
from functools import lru_cache
from typing import List

from pydantic import AnyUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    APP_NAME: str = "COSIB"
    APP_ENV: str = "development"  # development | staging | production
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_BASE_URL: str = "http://localhost:8000"
    FRONTEND_BASE_URL: str = "http://localhost:5173"

    # --- Security ---
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14
    PASSWORD_MIN_LENGTH: int = 8

    # --- Database ---
    DATABASE_URL: str = "postgresql+asyncpg://cosib:cosib@localhost:5432/cosib"
    DATABASE_URL_SYNC: str = "postgresql+psycopg2://cosib:cosib@localhost:5432/cosib"

    # --- CORS ---
    # Explicit production origin(s), comma-separated (e.g. your Vercel
    # production domain and any custom domain).
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    # Optional regex to additionally allow Vercel preview deployment URLs,
    # which get a unique subdomain per branch/PR (e.g.
    # cosib-frontend-git-feature-x-yourorg.vercel.app). Leave empty to
    # disable. Example: r"https://cosib-frontend.*\.vercel\.app"
    CORS_ORIGIN_REGEX: str = ""

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # --- Rate limiting ---
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_CHAT: str = "20/minute"
    RATE_LIMIT_AUTH: str = "10/minute"

    # --- AI Providers (used from ES-002 onward) ---
    AI_PROVIDER_DEFAULT: str = "mock"  # mock | gemini | openai
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # --- File uploads ---
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 15
    ALLOWED_UPLOAD_EXTENSIONS: str = "pdf,docx,txt"

    # --- Institution branding ---
    INSTITUTION_NAME: str = "Gateway ICT Polytechnic, Saapade"
    DEPARTMENT_NAME: str = "Computer Science Department"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
