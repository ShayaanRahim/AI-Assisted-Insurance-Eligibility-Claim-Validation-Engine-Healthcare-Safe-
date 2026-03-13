"""Application configuration"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application settings"""
    model_config = ConfigDict(env_file=".env")
    
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/claim_validation"


settings = Settings()
