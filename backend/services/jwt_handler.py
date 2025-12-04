"""
services/jwt_handler.py — работа с JWT токенами
"""
from datetime import datetime, timedelta
from typing import Optional
import jwt
from config import get_settings

# Получаем настройки
settings = get_settings()


def create_access_token(user_id: int, is_admin: bool, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создаёт JWT токен для пользователя
    
    СТАРОЕ имя функции (для совместимости)
    """
    return create_token(
        data={
            "user_id": user_id,
            "is_admin": is_admin
        },
        expires_delta=expires_delta
    )


def create_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создаёт JWT токен
    
    НОВОЕ имя функции (основная)
    """
    to_encode = data.copy()
    
    # Устанавливаем время истечения
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Кодируем токен
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Декодирует JWT токен и возвращает payload
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Токен истек
    except jwt.InvalidTokenError:
        return None  # Токен невалиден
