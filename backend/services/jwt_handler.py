"""
services/jwt_handler.py — создание и проверка JWT токенов
"""
import jwt
from datetime import datetime, timedelta
from typing import Optional
from config import get_settings

settings = get_settings()


def create_access_token(user_id: int, is_admin: bool = False) -> str:
    """
    Создать JWT токен
    
    Args:
        user_id: ID пользователя
        is_admin: является ли админом
    
    Returns:
        JWT токен
    """
    payload = {
        "user_id": user_id,
        "is_admin": is_admin,
        "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return token


def decode_token(token: str) -> Optional[dict]:
    """
    Декодировать и проверить JWT токен
    
    Args:
        token: JWT токен
    
    Returns:
        Payload если токен валиден, иначе None
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        print("Token expired")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token")
        return None


def get_user_id_from_token(token: str) -> Optional[int]:
    """Получить user_id из токена"""
    payload = decode_token(token)
    if payload:
        return payload.get("user_id")
    return None


def is_admin_token(token: str) -> bool:
    """Проверить, является ли токен админским"""
    payload = decode_token(token)
    if payload:
        return payload.get("is_admin", False)
    return False
