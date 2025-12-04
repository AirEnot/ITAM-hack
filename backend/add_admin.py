from database import SessionLocal
from models import Admin
from utils.security import hash_password
import os

# Подключаемся к БД
db = SessionLocal()

# Создаём админа
admin = Admin(
    email=f"{os.getenv("ADMIN_EMAIL")}",
    hashed_password=hash_password(f"{os.getenv("ADMIN_PASSWORD")}")
)

# Добавляем в БД
db.add(admin)
db.commit()

print("✅ Админ успешно добавлен!")
db.close()