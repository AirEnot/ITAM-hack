#!/usr/bin/env python3
"""
Скрипт для принудительного обновления пароля админа
Использование: python fix_admin_password.py
"""
from database import SessionLocal
from models import Admin
from utils.security import hash_password, verify_password
from config import get_settings

def main():
    """Принудительно обновляет пароль админа"""
    settings = get_settings()
    
    admin_email = settings.ADMIN_EMAIL
    admin_password = settings.ADMIN_PASSWORD
    
    print(f"🔧 Обновление пароля админа...")
    print(f"   Email: {admin_email}")
    print(f"   Новый пароль: {admin_password}")
    
    db = SessionLocal()
    
    try:
        # Ищем админа
        admin = db.query(Admin).filter(Admin.email == admin_email).first()
        
        if not admin:
            print(f"❌ Админ с email {admin_email} не найден!")
            print("   Создаю нового админа...")
            admin = Admin(
                email=admin_email,
                hashed_password=hash_password(admin_password)
            )
            db.add(admin)
        else:
            print(f"✅ Админ найден (id={admin.id})")
            print("   Обновляю пароль...")
            # Обновляем пароль
            admin.hashed_password = hash_password(admin_password)
        
        db.commit()
        db.refresh(admin)
        
        # Проверяем, что пароль работает
        if verify_password(admin_password, admin.hashed_password):
            print(f"✅ Пароль успешно обновлен и проверен!")
            print(f"   Email: {admin.email}")
            print(f"   ID: {admin.id}")
            print(f"\n📝 Теперь можно войти с:")
            print(f"   Email: {admin_email}")
            print(f"   Password: {admin_password}")
        else:
            print("❌ Ошибка: пароль не проходит проверку после обновления!")
            print("   Возможно, проблема с хешированием паролей")
                
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()

