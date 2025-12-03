"""
database.py — подключение SQLAlchemy к SQLite и инициализация БД
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from config import get_settings

settings = get_settings()

# SQLite engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # Нужна для SQLite
    echo=False  # Поставьте True для отладки SQL запросов
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base для всех моделей
Base = declarative_base()


# Включить foreign keys в SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def get_db() -> Session:
    """Зависимость для получения сессии БД в роутерах"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Инициализировать все таблицы"""
    from models import User, Hackathon, Team, TeamMember, Invitation, Admin, UserHackathon
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully!")
