"""
config.py — конфигурация приложения, переменные окружения
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Конфигурация приложения"""
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = "8270383153:AAH1fGA0U9JuSUA8Qc1-f4vvhXodLK2z2tw"
    TELEGRAM_BOT_USERNAME: str = "bdc_itam_hack_bot"
    # JWT
    SECRET_KEY: str = "e1d083f7a30901221bd417ece379627f95ff5765a02d0c45eb89c4e9576a2134"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 часа
    
    # Admin
    ADMIN_EMAIL: str = "at@tt.com"
    ADMIN_PASSWORD: str = "111111"
    
    # Database
    DATABASE_URL: str = "sqlite:///./database.sqlite"
    
    # API
    API_PREFIX: str = "/api"
    
    # Авторизация
    CODE_EXPIRY_MINUTES: int = 10 

    # CORS - можно передать через переменную окружения как строку через запятую
    ALLOWED_ORIGINS: str = "http://0.0.0.0:3000,http://0.0.0.0:8080,http://0.0.0.0:5173,http://0.0.0.0:80,http://0.0.0.0,http://localhost:3000,http://localhost:5173,http://localhost:80,http://localhost,https://itam-hack-production-2c4b.up.railway.app,https://itam-hack-production.up.railway.app"
    
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
