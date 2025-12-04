"""
utils/security.py — хеширование паролей и проверка подписей
"""
from passlib.context import CryptContext
import hashlib
import hmac
from config import get_settings

settings = get_settings()

# Для хеширования паролей админов
# Используем pbkdf2_sha256, чтобы избежать проблем с bcrypt версией и ограничением в 72 байта
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    """Хешировать пароль"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверить пароль"""
    return pwd_context.verify(plain_password, hashed_password)


def verify_telegram_signature(init_data: str) -> bool:
    """
    Проверить подпись инициализации Telegram Mini App
    
    Args:
        init_data: строка вида "user=...&hash=...&..."
    
    Returns:
        True если подпись корректна
    """
    try:
        # Парсим init_data
        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(
                [item.split("=") for item in init_data.split("&") if item.split("=")[0] != "hash"]
            )
        )
        
        # Получаем хеш из init_data
        secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
        hash_received = dict(item.split("=") for item in init_data.split("&"))["hash"]
        
        # Вычисляем ожидаемый хеш
        hash_calculated = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hash_calculated == hash_received
    except Exception as e:
        print(f"Error verifying Telegram signature: {e}")
        return False
