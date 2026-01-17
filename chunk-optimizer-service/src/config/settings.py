"""Application settings"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    database_url: str = "postgresql://postgres:postgres@localhost:5432/chunk_optimizer"
    redis_url: str = "redis://localhost:6379/0"
    log_level: str = "INFO"
    
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
