import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "NEXUS — Society Maintenance Tracker"
    API_V1_STR: str = "/api"
    
    # Target DB: PostgreSQL ready, SQLite local default
    default_db_path: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "nexus.db")).replace("\\", "/")
    
    @property
    def async_database_url(self) -> str:
        url = os.getenv("DATABASE_URL")
        if not url:
            return f"sqlite+aiosqlite:///{self.default_db_path}"
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    DATABASE_URL: str = ""
    
    def __init__(self, **values):
        super().__init__(**values)
        if not self.DATABASE_URL:
            self.DATABASE_URL = self.async_database_url
    
    # JWT Auth
    JWT_SECRET: str = os.getenv("JWT_SECRET", "nexus_super_secret_jwt_key_2026_change_in_prod")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Notifications & LLM (Optional keys with fallbacks)
    RESEND_API_KEY: Optional[str] = os.getenv("RESEND_API_KEY", None)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY", None)

    class Config:
        case_sensitive = True

settings = Settings()
