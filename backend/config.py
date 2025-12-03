"""
config.py — конфигурация приложения, переменные окружения
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Конфигурация приложения"""
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = "your_token_here"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-min-32-chars-long"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 часа
    
    # Admin
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "secure_password_change_me"
    
    # Database
    DATABASE_URL: str = "sqlite:///./database.sqlite"
    
    # API
    API_PREFIX: str = "/api"
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
