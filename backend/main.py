"""
main.py — главный файл FastAPI приложения
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from config import get_settings
from database import init_db
import logging

# Импортируем роутеры
from routers import auth, users, hackathons, teams, invitations, admin

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

# Инициализируем приложение
app = FastAPI(
    title="Hackathon Team Platform API",
    description="API для платформы поиска и формирования команд хакатонов",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализируем БД при старте приложения
@app.on_event("startup")
async def startup_event():
    """Инициализировать БД при запуске приложения"""
    try:
        init_db()
        logger.info("✅ Database initialized")
        
        # Выводим информацию об админах
        from database import SessionLocal
        from models import Admin
        
        db = SessionLocal()
        try:
            all_admins = db.query(Admin).all()
            if all_admins:
                logger.info("="*60)
                logger.info("📋 ИНФОРМАЦИЯ ОБ АДМИНИСТРАТОРАХ:")
                logger.info("="*60)
                for admin in all_admins:
                    # Для админа из настроек показываем пароль, для остальных - ***
                    admin_password = settings.ADMIN_PASSWORD if admin.email == settings.ADMIN_EMAIL else "***"
                    logger.info(f"  👤 Email: {admin.email}")
                    logger.info(f"     Password: {admin_password}")
                    logger.info(f"     ID: {admin.id}")
                logger.info("="*60)
            else:
                logger.warning("⚠️  Администраторы не найдены")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")

# Включаем роутеры участника и админа
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(hackathons.router)
app.include_router(teams.router)
app.include_router(invitations.router)
app.include_router(admin.router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Hackathon Team Platform API",
        "docs": "/docs",
        "version": "1.0.0"
    }

# Health check
@app.get("/health")
async def health():
    return {"status": "ok"}

# Error handler для необработанных исключений
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    # HTTPException обрабатывается FastAPI автоматически с CORS заголовками
    from fastapi import HTTPException
    if isinstance(exc, HTTPException):
        raise exc
    
    import traceback
    logger.error(f"Unhandled error: {exc}")
    logger.error(traceback.format_exc())
    
    # Возвращаем ответ с CORS заголовками
    from fastapi.responses import JSONResponse
    response = JSONResponse(
        status_code=500,
        content={"detail": str(exc) if str(exc) else "Internal server error"}
    )
    # Добавляем CORS заголовки
    origin = request.headers.get("origin")
    if origin and origin in settings.get_allowed_origins():
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )
