"""
config.py — конфигурация приложения, переменные окружения
"""
import os
from functools import lru_cache
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()


class Settings:
    """Конфигурация приложения"""
    
    def __init__(self):
        # Telegram
        self.TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.TELEGRAM_BOT_USERNAME: str = os.getenv("TELEGRAM_BOT_USERNAME", "")
        
        # JWT
        self.SECRET_KEY: str = os.getenv("SECRET_KEY", "")
        self.ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
        
        # Admin
        self.ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "")
        self.ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "")
        
        # Database
        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./database.sqlite")
        
        # API
        self.API_PREFIX: str = os.getenv("API_PREFIX", "/api")
        self.BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
        self.FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
        
        # Авторизация
        self.CODE_EXPIRY_MINUTES: int = int(os.getenv("CODE_EXPIRY_MINUTES", "10"))
        
        # CORS - можно передать через переменную окружения как строку через запятую
        self.ALLOWED_ORIGINS: str = os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:3000,http://localhost:3001,http://localhost:5173,http://localhost:8000"
        )
    
    def get_allowed_origins(self) -> list:
        """Преобразует строку ALLOWED_ORIGINS в список"""
        if isinstance(self.ALLOWED_ORIGINS, list):
            return self.ALLOWED_ORIGINS
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
