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

router = APIRouter(prefix="/api/debug", tags=["debug"])

@router.get("/api/debug/db-info")
async def db_info():
    """Временный endpoint для отладки БД"""
    from database import SessionLocal
    from models import Admin, User
    
    db = SessionLocal()
    try:
        admins_count = db.query(Admin).count()
        users_count = db.query(User).count()
        
        return {
            "database": "SQLite",
            "admins_count": admins_count,
            "users_count": users_count,
            "admins": [
                {"id": a.id, "email": a.email} 
                for a in db.query(Admin).all()
            ]
        }
    finally:
        db.close()