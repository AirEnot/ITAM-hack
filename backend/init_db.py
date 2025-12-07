#!/usr/bin/env python3
"""
Скрипт для инициализации БД (работает в Docker и локально)
"""
import os
import sys

# Определяем путь к директории data
# В Docker: /app/data, локально: ./data
if os.path.exists("/app"):
    # Docker контейнер
    data_dir = "/app/data"
else:
    # Локальная разработка
    data_dir = os.path.join(os.getcwd(), "data")

# Убеждаемся, что директория data существует
os.makedirs(data_dir, exist_ok=True)

# Изменяем DATABASE_URL на путь в data, если не задан через env
current_db_url = os.environ.get("DATABASE_URL", "")
if not current_db_url or current_db_url == "sqlite:///./database.sqlite":
    if os.path.exists("/app"):
        # Docker
        os.environ["DATABASE_URL"] = "sqlite:///./data/database.sqlite"
    else:
        # Локально
        os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(data_dir, 'database.sqlite')}"

from database import init_db
from models import Admin
from database import SessionLocal
from utils.security import hash_password
from config import get_settings

def main():
    """Инициализирует БД и создает админа"""
    print("🔄 Инициализация базы данных...")
    
    try:
        # Инициализируем БД
        init_db()
        print("✅ База данных инициализирована")
        
        # Создаем админа
        settings = get_settings()
        
        # Отладочный вывод - показываем, какие значения используются
        print(f"\n🔍 Отладка: Используемые настройки админа:")
        print(f"   ADMIN_EMAIL из config: {settings.ADMIN_EMAIL}")
        print(f"   ADMIN_PASSWORD из config: {settings.ADMIN_PASSWORD}")
        print(f"   Переменные окружения ADMIN_EMAIL: {os.environ.get('ADMIN_EMAIL', 'не задана')}")
        print(f"   Переменные окружения ADMIN_PASSWORD: {os.environ.get('ADMIN_PASSWORD', 'не задана')}\n")
        
        db = SessionLocal()
        
        try:
            # Проверяем, есть ли уже админ
            existing_admin = db.query(Admin).filter(Admin.email == settings.ADMIN_EMAIL).first()
            if existing_admin:
                # Обновляем пароль админа на актуальный из настроек
                existing_admin.hashed_password = hash_password(settings.ADMIN_PASSWORD)
                db.commit()
                print(f"✅ Пароль админа обновлен: {settings.ADMIN_EMAIL}")
            else:
                # Создаем нового админа
                admin = Admin(
                    email=settings.ADMIN_EMAIL,
                    hashed_password=hash_password(settings.ADMIN_PASSWORD)
                )
                db.add(admin)
                db.commit()
                print(f"✅ Админ создан: {settings.ADMIN_EMAIL}")
            
            # Выводим информацию о всех админах
            print("\n" + "="*60)
            print("📋 ИНФОРМАЦИЯ ОБ АДМИНИСТРАТОРАХ:")
            print("="*60)
            all_admins = db.query(Admin).all()
            if all_admins:
                for admin in all_admins:
                    # Проверяем, соответствует ли пароль из настроек этому админу
                    admin_password = settings.ADMIN_PASSWORD if admin.email == settings.ADMIN_EMAIL else "***"
                    print(f"  👤 Email: {admin.email}")
                    print(f"     Password: {admin_password}")
                    print(f"     ID: {admin.id}")
                    print()
            else:
                print("  ⚠️  Администраторы не найдены")
            print("="*60 + "\n")
            
        except Exception as e:
            db.rollback()
            print(f"⚠️  Ошибка при создании админа: {e}")
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

