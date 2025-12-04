"""
routers/auth.py — аутентификация (Telegram + Admin)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from datetime import timedelta
from database import get_db
from models import User, Admin
from schemas import TelegramAuthRequest, AdminLoginRequest, TokenResponse
from services.jwt_handler import create_access_token, create_token
from services.telegram_auth import create_auth_code, verify_auth_code
from utils.security import verify_password
from config import get_settings

settings = get_settings()

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ════════════════════════════════════════════
# БЫСТРАЯ АВТОРИЗАЦИЯ ЧЕРЕЗ TELEGRAM
# ════════════════════════════════════════════

@router.post("/telegram", response_model=TokenResponse)
async def telegram_auth(request: TelegramAuthRequest, db: Session = Depends(get_db)):
    """
    Регистрация/вход через Telegram
    """
    
    existing_user = db.query(User).filter(
        User.telegram_id == request.telegram_id
    ).first()
    
    if existing_user:
        existing_user.telegram_username = request.telegram_username
        existing_user.avatar_url = request.avatar_url
        db.commit()
        
        token = create_access_token(user_id=existing_user.id, is_admin=False)
        return TokenResponse(
            access_token=token,
            user_id=existing_user.id
        )
    
    new_user = User(
        telegram_id=request.telegram_id,
        telegram_username=request.telegram_username,
        full_name=request.full_name,
        avatar_url=request.avatar_url,
        skills="[]",
        experience_level="junior"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    token = create_access_token(user_id=new_user.id, is_admin=False)
    return TokenResponse(
        access_token=token,
        user_id=new_user.id
    )


# ════════════════════════════════════════════
# АВТОРИЗАЦИЯ АДМИНА
# ════════════════════════════════════════════

@router.post("/admin/login", response_model=TokenResponse)
async def admin_login(request: AdminLoginRequest, db: Session = Depends(get_db)):
    """
    Вход админа через email и пароль
    """
    admin = db.query(Admin).filter(Admin.email == request.email).first()
    
    if not admin or not verify_password(request.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    token = create_access_token(user_id=admin.id, is_admin=True)
    return TokenResponse(
        access_token=token,
        user_id=admin.id
    )


# ════════════════════════════════════════════
# АВТОРИЗАЦИЯ ЧЕРЕЗ ТГ БОТА С КОДОМ
# ════════════════════════════════════════════

@router.get("/telegram/bot-link")
def get_telegram_bot_link():
    """
    Возвращает ссылку на ТГ бота
    """
    return {
        "bot_link": f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}",
        "bot_username": settings.TELEGRAM_BOT_USERNAME,
        "message": "Нажмите на ссылку и начните с /start"
    }


@router.post("/telegram/generate-code")
def generate_telegram_code(
    telegram_id: str,
    telegram_username: str | None = None,
    db: Session = Depends(get_db)
):
    """
    Генерирует код авторизации для пользователя ТГ
    """
    
    code = create_auth_code(
        telegram_id=telegram_id,
        telegram_username=telegram_username,
        db=db
    )
    
    return {
        "code": code,
        "message": f"Ваш код: {code}\n\nВставьте этот код на сайте чтобы авторизоваться"
    }

@router.post("/telegram/verify-code")
def verify_telegram_code(
    code: str = Body(..., embed=True),
    db: Session = Depends(get_db),
):
    """
    Проверяет код авторизации и возвращает JWT токен
    """
    
    user_data = verify_auth_code(code=code, db=db)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или истекший код"
        )
    
    access_token = create_token(
        data={
            "user_id": user_data["user_id"],
            "is_admin": False
        },
        expires_delta=timedelta(hours=24)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }