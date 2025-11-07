"""
Configuration module for Written AI Chatbot
Handles environment variables and application settings
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Flask Configuration
    flask_env: str = "development"
    flask_debug: bool = True
    flask_host: str = "127.0.0.1"
    flask_port: int = 5000
    secret_key: str = "dev-secret-key-change-in-production"
    
    # Database Configuration
    database_url: str = "sqlite:///written.db"
    
    # PostgreSQL specific settings (when not using database_url)
    postgres_host: str = "localhost"
    postgres_port: int = 5433
    postgres_user: str = "postgres"
    postgres_password: str = "password"
    postgres_db: str = "test"
    
    # AI Service Configuration
    # Primary Provider (Required)
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.5-flash"
    primary_ai_provider: str = "gemini"
    
    # Optional Providers (for fallback support)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-sonnet-20240229"
    
    # Taiga API Configuration
    taiga_base_url: str = "<project_url>"
    taiga_username: Optional[str] = None
    taiga_password: Optional[str] = None
    taiga_auth_token: Optional[str] = None
    
    # Application Settings
    log_level: str = "INFO"
    default_activity_prompt: str = "Generate a professional daily activity description based on the following information:"
    max_activity_length: int = 500
    max_requests_per_hour: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
