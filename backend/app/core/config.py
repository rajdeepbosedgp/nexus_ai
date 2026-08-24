import os
from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "NEXUS — Society Maintenance Tracker"
    API_V1_STR: str = "/api"
    
    DATABASE_URL: str = ""

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str]) -> str:
        if not v:
            default_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..", "nexus.db")
            ).replace("\\", "/")
            return f"sqlite+aiosqlite:///{default_path}"
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        if v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v
    
    JWT_SECRET: str = os.getenv("JWT_SECRET", "nexus_super_secret_jwt_key_2026_change_in_prod")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    RESEND_API_KEY: Optional[str] = os.getenv("RESEND_API_KEY", None)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY", None)

    class Config:
        case_sensitive = True

settings = Settings()
