from database import SessionLocal
from models import Admin
from utils.security import hash_password
from config import get_settings
from sqlalchemy.exc import IntegrityError


def main():
    """
    Создаёт администратора в БД, используя настройки из config.py / .env
    """
    settings = get_settings()

    admin_email = settings.ADMIN_EMAIL
    admin_password = settings.ADMIN_PASSWORD

    # bcrypt поддерживает максимум 72 байта пароля
    if len(admin_password.encode("utf-8")) > 72:
        print("⚠️ Пароль администратора длиннее 72 байт, он будет обрезан до 72 байт для bcrypt.")
        admin_password = admin_password.encode("utf-8")[:72].decode("utf-8", errors="ignore")

    db = SessionLocal()

    try:
        # Проверяем, нет ли уже такого админа
        existing_admin = db.query(Admin).filter(Admin.email == admin_email).first()
        if existing_admin:
            print(f"⚠️ Админ с email {admin_email} уже существует (id={existing_admin.id})")
            return

        # Создаём админа
        admin = Admin(
            email=admin_email,
            hashed_password=hash_password(admin_password),
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print(f"✅ Админ успешно добавлен! id={admin.id}, email={admin.email}")
    except IntegrityError as e:
        db.rollback()
        print(f"❌ Ошибка целостности БД при добавлении админа: {e}")
    except Exception as e:
        db.rollback()
        print(f"❌ Не удалось создать админа: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()