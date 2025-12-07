@app.get("/api/debug/db-info")
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