import os
import logging
from typing import Optional
from pydantic import BaseModel

logger = logging.getLogger("enterprise-workflow.config")

class AppConfig(BaseModel):
    environment: str = os.getenv("APP_ENV", "production")
    database_url: Optional[str] = os.getenv("DATABASE_URL")
    api_secret_key: str = os.getenv("SECRET_KEY", "default-dev-secret-change-in-production")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")

    def is_postgres(self) -> bool:
        return bool(self.database_url and self.database_url.startswith("postgres"))

config = AppConfig()
