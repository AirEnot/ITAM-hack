import secrets
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import AuthCode, User
from config import get_settings

settings = get_settings()


def generate_code() -> str:
    """Генерирует 6-значный код"""
    return ''.join(secrets.choice(string.digits) for _ in range(6))


def create_auth_code(
    telegram_id: str,
    telegram_username: str,
    db: Session
) -> str:
    """Создаёт код авторизации"""
    
    # Генерируем код
    code = generate_code()
    
    # Вычисляем время истечения
    expires_at = datetime.utcnow() + timedelta(minutes=settings.CODE_EXPIRY_MINUTES)
    
    # Создаём запись в БД
    auth_code = AuthCode(
        code=code,
        telegram_id=telegram_id,
        telegram_username=telegram_username,
        expires_at=expires_at
    )
    
    db.add(auth_code)
    db.commit()
    
    return code


def verify_auth_code(code: str, db: Session) -> dict | None:
    """Проверяет код и возвращает данные пользователя если валиден"""
    
    # Ищем код в БД
    auth_code = db.query(AuthCode).filter(AuthCode.code == code).first()
    
    if not auth_code:
        return None  # Код не найден
    
    if not auth_code.is_valid():
        return None  # Код истек или уже использован
    
    # Помечаем код как использованный
    auth_code.is_used = True
    
    # Ищем или создаём пользователя
    user = db.query(User).filter(User.telegram_id == auth_code.telegram_id).first()
    
    if not user:
        # Создаём нового пользователя
        user = User(
            telegram_id=auth_code.telegram_id,
            telegram_username=auth_code.telegram_username,
            full_name=auth_code.telegram_username or f"User_{auth_code.telegram_id}"
        )
        db.add(user)
    
    db.commit()
    
    return {
        "user_id": user.id,
        "telegram_id": user.telegram_id,
        "telegram_username": user.telegram_username,
        "full_name": user.full_name
    }
