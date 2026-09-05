from pydantic_settings import BaseSettings
from typing import Optional
import os

# Absolute default: <backend>/revenue_recover.db regardless of launch CWD.
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEFAULT_DB = f"sqlite:///{os.path.join(_BACKEND_DIR, 'revenue_recover.db')}"


class Settings(BaseSettings):
    # Local-first: SQLite runs with zero setup. Override with Postgres via .env.
    DATABASE_URL: str = _DEFAULT_DB
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4"
    DEMO_MODE: bool = True
    MAX_RETRIES: int = 3
    MAX_CONTACTS_PER_WEEK: int = 2
    MANUAL_REVIEW_THRESHOLD: float = 100000.0
    ALLOWED_CONTACT_START_HOUR: int = 8
    ALLOWED_CONTACT_END_HOUR: int = 20
    APP_NAME: str = "RevenueRecover AI"
    DEBUG: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
