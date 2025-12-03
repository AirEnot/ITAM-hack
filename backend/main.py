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
from routers import auth, users, hackathons, teams

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
    allow_origins=settings.ALLOWED_ORIGINS,
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
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")

# Включаем роутеры
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(hackathons.router)
app.include_router(teams.router)

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

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )
