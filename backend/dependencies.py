"""
dependencies.py — зависимости для FastAPI (текущий пользователь, права)
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from database import get_db
from models import User, Admin
from services.jwt_handler import decode_token


security = HTTPBearer()


async def get_current_user(
    credentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Получить текущего пользователя из JWT токена
    Проверяет что это участник, не админ
    """
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload or payload.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or insufficient permissions"
        )
    
    user_id = payload.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


async def get_current_admin(
    credentials = Depends(security),
    db: Session = Depends(get_db)
) -> Admin:
    """
    Получить текущего админа из JWT токена
    Проверяет что это админ
    """
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload or not payload.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    admin_id = payload.get("user_id")
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin not found"
        )
    
    return admin
