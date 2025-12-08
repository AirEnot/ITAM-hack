"""
config.py — конфигурация приложения, переменные окружения
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Конфигурация приложения"""
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_BOT_USERNAME: str = ""
    # JWT
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 часа
    
    # Admin
    ADMIN_EMAIL: str = ""
    ADMIN_PASSWORD: str = ""
    
    # Database
    DATABASE_URL: str = "sqlite:///./database.sqlite"
    
    # API
    API_PREFIX: str = "/api"
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Авторизация
    CODE_EXPIRY_MINUTES: int = 10 

    # CORS - можно передать через переменную окружения как строку через запятую
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://localhost:5173,http://localhost:8000"
    
    def get_allowed_origins(self) -> list:
        """Преобразует строку ALLOWED_ORIGINS в список"""
        if isinstance(self.ALLOWED_ORIGINS, list):
            return self.ALLOWED_ORIGINS
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
