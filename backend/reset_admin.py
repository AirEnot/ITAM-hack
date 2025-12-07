"""
Скрипт для пересоздания админа с новым паролем
Использование: python reset_admin.py
"""
from database import SessionLocal
from models import Admin
from utils.security import hash_password, verify_password
from config import get_settings

def main():
    """Пересоздает админа с паролем из настроек"""
    settings = get_settings()
    
    admin_email = settings.ADMIN_EMAIL
    admin_password = settings.ADMIN_PASSWORD
    
    db = SessionLocal()
    
    try:
        # Ищем существующего админа
        existing_admin = db.query(Admin).filter(Admin.email == admin_email).first()
        
        if existing_admin:
            # Обновляем пароль
            existing_admin.hashed_password = hash_password(admin_password)
            db.commit()
            db.refresh(existing_admin)
            
            # Проверяем, что пароль работает
            if verify_password(admin_password, existing_admin.hashed_password):
                print(f"✅ Админ обновлен и пароль проверен!")
                print(f"   Email: {existing_admin.email}")
                print(f"   ID: {existing_admin.id}")
            else:
                print("❌ Ошибка: пароль не проходит проверку после обновления")
        else:
            # Создаем нового админа
            admin = Admin(
                email=admin_email,
                hashed_password=hash_password(admin_password)
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            
            # Проверяем пароль
            if verify_password(admin_password, admin.hashed_password):
                print(f"✅ Админ создан и пароль проверен!")
                print(f"   Email: {admin.email}")
                print(f"   ID: {admin.id}")
            else:
                print("❌ Ошибка: пароль не проходит проверку после создания")
                
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()

