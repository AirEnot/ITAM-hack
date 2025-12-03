"""
routers/auth.py — аутентификация (Telegram + Admin)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, Admin
from schemas import TelegramAuthRequest, AdminLoginRequest, TokenResponse
from services.jwt_handler import create_access_token
from utils.security import verify_password, hash_password
import json

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/telegram", response_model=TokenResponse)
async def telegram_auth(request: TelegramAuthRequest, db: Session = Depends(get_db)):
    """
    Регистрация/вход через Telegram
    
    На фронте получить данные можно так:
    - Если используется Telegram Mini App: window.Telegram.WebApp.initData
    - Иначе: просто отправить telegram_id, username и имя
    
    В реальности нужно проверить подпись через verify_telegram_signature(),
    но для MVP можно упростить.
    """
    
    # Проверяем что пользователь с таким telegram_id уже есть
    existing_user = db.query(User).filter(
        User.telegram_id == request.telegram_id
    ).first()
    
    if existing_user:
        # Обновляем данные если изменились
        existing_user.telegram_username = request.telegram_username
        existing_user.avatar_url = request.avatar_url
        db.commit()
        
        token = create_access_token(user_id=existing_user.id, is_admin=False)
        return TokenResponse(
            access_token=token,
            user_id=existing_user.id
        )
    
    # Создаем нового пользователя
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
