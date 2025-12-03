# 🚀 Hackathon Team Platform — Backend

Полнофункциональный REST API для платформы поиска и формирования команд хакатонов с использованием FastAPI и SQLite.


---

## 📋 Содержание

1. [Быстрый старт](#-быстрый-старт)
2. [Установка](#-установка)
3. [Структура проекта](#-структура-проекта)
4. [API Документация](#-api-документация)
5. [Развертывание](#-развертывание)
6. [Интеграция с фронтом](#-интеграция-с-фронтом)
7. [Решение проблем](#-решение-проблем)

---

## 🚀 Быстрый старт

### Вариант 1: Локально (разработка)

```bash
# 1. Клонировать и перейти в папку
git clone <repo-url>
cd backend

# 2. Создать virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или venv\Scripts\activate  # Windows

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Создать .env файл (скопировать из .env.example)
cp .env.example .env

# 5. Инициализировать БД
python -c "from database import init_db; init_db()"

# 6. Запустить сервер
uvicorn main:app --reload --port 8000

# 7. Открыть документацию
# http://localhost:8000/docs
```

### Вариант 2: Docker (требует Docker и Docker Compose)

```bash
# 1. Создать .env из .env.example
cp .env.example .env

# 2. Запустить контейнеры
docker-compose up -d

# 3. Проверить логи
docker-compose logs -f backend

# 4. Остановить
docker-compose down
```

---

## 📦 Установка

### Требования

- **Python 3.10+**
- **pip** (package manager)
- **git** (для клонирования)

### Пошаговая установка

#### 1. Клонировать репозиторий

```bash
git clone <repository-url>
cd hackathon-team-platform/backend
```

#### 2. Создать виртуальное окружение

```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

#### 3. Обновить pip

```bash
pip install --upgrade pip
```

#### 4. Установить зависимости

```bash
pip install -r requirements.txt
```

#### 5. Настроить переменные окружения

```bash
# Создать файл .env
cp .env.example .env

# Отредактировать .env с вашими значениями:
# - TELEGRAM_BOT_TOKEN (получить у @BotFather)
# - SECRET_KEY (сгенерировать: openssl rand -hex 32)
# - ADMIN_EMAIL и ADMIN_PASSWORD (для первого входа)
```

#### 6. Инициализировать БД

```bash
python -c "from database import init_db; init_db()"

# Или более подробно:
python
>>> from database import init_db
>>> init_db()
>>> exit()
```

#### 7. Создать первого админа

```bash
python

from database import SessionLocal
from models import Admin
from utils.security import hash_password

db = SessionLocal()
admin = Admin(
    email="admin@example.com",
    hashed_password=hash_password("your_secure_password")
)
db.add(admin)
db.commit()
print("✅ Admin created!")
db.close()
```

#### 8. Запустить сервер

```bash
uvicorn main:app --reload --port 8000
```

**Вывод должен быть:**
```
INFO:     Started server process [1234]
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete
✅ Database initialized
```

#### 9. Проверить что всё работает

Откройте в браузере: **http://localhost:8000**

Должны увидеть JSON ответ:
```json
{
  "message": "Hackathon Team Platform API",
  "docs": "/docs",
  "version": "1.0.0"
}
```

Документация: **http://localhost:8000/docs** (Swagger UI)

---

## 📂 Структура проекта

```
backend/
├── main.py                 # Главный файл приложения FastAPI
├── config.py              # Конфигурация (переменные окружения)
├── database.py            # Подключение БД, инициализация
├── models.py              # SQLAlchemy ORM модели
├── schemas.py             # Pydantic схемы (Request/Response)
├── dependencies.py        # Зависимости (auth, permissions)
│
├── routers/               # REST API роутеры по доменам
│   ├── __init__.py
│   ├── auth.py            # Аутентификация (Telegram, Admin)
│   ├── users.py           # Управление профилем
│   ├── hackathons.py      # Хакатоны (для админа и участников)
│   ├── teams.py           # Управление командами
│   ├── invitations.py     # Приглашения в команду
│   └── admin.py           # Админ-панель, аналитика
│
├── services/              # Бизнес-логика, сервисы
│   ├── __init__.py
│   ├── jwt_handler.py     # Работа с JWT токенами
│   ├── telegram_auth.py   # Проверка подписей Telegram (optional)
│   └── analytics.py       # Подсчёт статистики
│
├── utils/                 # Утилиты
│   ├── __init__.py
│   ├── security.py        # Хеширование паролей
│   └── validators.py      # Валидация данных
│
├── requirements.txt       # Python зависимости
├── .env.example          # Пример переменных окружения
├── database.sqlite       # SQLite БД (создается автоматически)
├── Dockerfile            # Docker контейнер
├── docker-compose.yml    # Docker Compose конфигурация
├── README.md             # Этот файл
├── ACTION_PLAN.md        # Детальный план разработки
└── FRONTEND_INTEGRATION.md  # Гайд интеграции с фронтом
```

---

## 📡 API Документация

### Автоматическая документация

После запуска сервера откройте:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Там можно протестировать все эндпоинты прямо из браузера.

### Основные категории эндпоинтов

#### 🔐 Аутентификация (`/api/auth`)

| Метод | Путь | Описание |
|-------|------|---------|
| POST | `/api/auth/telegram` | Регистрация участника через Telegram |
| POST | `/api/admin/login` | Вход админа (email + пароль) |

#### 👤 Профиль (`/api/users`)

| Метод | Путь | Описание |
|-------|------|---------|
| GET | `/api/users/me` | Получить свой профиль |
| PUT | `/api/users/me` | Обновить свой профиль |
| GET | `/api/users/{id}` | Получить профиль другого пользователя |
| GET | `/api/users/hackathons/{id}/participants` | Список участников хакатона |

#### 🎯 Хакатоны (`/api/hackathons`)

| Метод | Путь | Описание |
|-------|------|---------|
| GET | `/api/hackathons` | Список хакатонов |
| GET | `/api/hackathons/{id}` | Инфо о хакатоне |
| POST | `/api/hackathons/{id}/register` | Зарегистрироваться на хакатон |

#### 👥 Команды (`/api/teams`)

| Метод | Путь | Описание |
|-------|------|---------|
| POST | `/api/teams` | Создать команду |
| GET | `/api/teams/{id}` | Инфо о команде |
| GET | `/api/teams/hackathons/{id}` | Команды хакатона |
| POST | `/api/teams/{id}/invite` | Пригласить в команду |
| DELETE | `/api/teams/{id}/members/{uid}` | Удалить члена |

#### 💌 Приглашения (`/api/invitations`)

| Метод | Путь | Описание |
|-------|------|---------|
| GET | `/api/invitations` | Мои приглашения |
| POST | `/api/invitations/{id}/accept` | Принять/отклонить |

#### 📊 Админ (`/api/admin`)

| Метод | Путь | Описание |
|-------|------|---------|
| GET | `/api/admin/hackathons` | Все хакатоны |
| POST | `/api/admin/hackathons` | Создать хакатон |
| GET | `/api/admin/{id}/analytics` | Аналитика |
| GET | `/api/admin/{id}/participants/export` | Экспорт CSV |
| GET | `/api/admin/{id}/teams/export` | Экспорт CSV |

---

## 🐳 Развертывание

### Docker (локально или на сервере)

#### Требования

- Docker
- Docker Compose

#### Процесс

```bash
# 1. Настроить .env
cp .env.example .env

# 2. Собрать и запустить
docker-compose up -d

# 3. Проверить статус
docker-compose ps

# 4. Посмотреть логи
docker-compose logs -f backend

# 5. Остановить
docker-compose down

# 6. Очистить
docker-compose down -v  # с удалением volumes
```

### Продакшн (рекомендации)

- [ ] Использовать **PostgreSQL** вместо SQLite
- [ ] Включить **HTTPS** (Let's Encrypt)
- [ ] Настроить **Nginx** как reverse proxy
- [ ] Использовать **Gunicorn** вместо Uvicorn
- [ ] Настроить **rate limiting** (slowapi)
- [ ] Логирование в **ELK Stack** или CloudWatch
- [ ] Мониторинг **Prometheus + Grafana**
- [ ] Резервные копии БД

Пример Dockerfile для продакшена:

```dockerfile
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH

CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker"]
```

---

## 🔌 Интеграция с фронтом

### Для фронтендера

Смотрите **FRONTEND_INTEGRATION.md** для полной документации о:
- Как отправлять запросы
- Как использовать JWT токены
- Примеры кода на JavaScript/React
- Error handling
- Безопасность

### Основной паттерн

```javascript
// 1. Получить токен (auth)
const token = localStorage.getItem('access_token');

// 2. Отправить запрос с Authorization header
fetch('/api/users/me', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})

// 3. Обработать ответ и показать UI
```

---

## 🧪 Тестирование

### Через Swagger UI

1. Откройте http://localhost:8000/docs
2. Найдите эндпоинт
3. Нажмите "Try it out"
4. Заполните параметры
5. Нажмите "Execute"

### Через Postman

1. Скачайте Postman
2. Импортируйте OpenAPI схему: http://localhost:8000/openapi.json
3. Тестируйте запросы

### Через curl (командная строка)

```bash
# Регистрация участника
curl -X POST http://localhost:8000/api/auth/telegram \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": 123456789,
    "telegram_username": "testuser",
    "full_name": "Test User"
  }'

# Использовать токен
TOKEN="your_access_token_here"
curl -X GET http://localhost:8000/api/users/me \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔍 Мониторинг и логирование

### Логи в консоли

```bash
# Более подробные логи
uvicorn main:app --reload --log-level debug
```

### Логи в файл

```python
# В main.py добавить:
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

---

## ⚠️ Решение проблем

### БД ошибки

**Проблема:** `sqlite3.OperationalError: database is locked`

**Решение:** Удалить database.sqlite и пересоздать:
```bash
rm database.sqlite
python -c "from database import init_db; init_db()"
```

### Import ошибки

**Проблема:** `ModuleNotFoundError: No module named 'fastapi'`

**Решение:** Убедитесь что активирован venv и установлены зависимости:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### CORS ошибки

**Проблема:** `Access to XMLHttpRequest has been blocked by CORS policy`

**Решение:** Добавить домен в `.env`:
```
ALLOWED_ORIGINS=http://localhost:3000,http://yourfrontend.com
```

### Токен истек

**Проблема:** `{"detail": "Invalid token"}`

**Решение:** Увеличить время жизни в `.env`:
```
ACCESS_TOKEN_EXPIRE_MINUTES=2880  # 48 часов
```

### Port занят

**Проблема:** `OSError: [Errno 48] Address already in use`

**Решение:** Использовать другой порт:
```bash
uvicorn main:app --port 8001
```

Или убить процесс:
```bash
# Linux/Mac
lsof -i :8000
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## 📚 Полезные ресурсы

- [FastAPI документация](https://fastapi.tiangolo.com/)
- [SQLAlchemy документация](https://docs.sqlalchemy.org/)
- [Pydantic документация](https://docs.pydantic.dev/)
- [JWT.io](https://jwt.io/)
- [Telegram Bot API](https://core.telegram.org/bots/api)

---

## 🤝 Контрибьютинг

1. Fork репозиторий
2. Create branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📝 Лицензия

MIT License - смотрите LICENSE файл

---

## 👨‍💼 Автор

Создано для ITAM Hackathon Community

---

## 🚧 Дорожная карта (TODO)

- [ ] WebSocket для real-time уведомлений
- [ ] Full-text поиск по участникам
- [ ] Система рейтинга
- [ ] Email уведомления
- [ ] Telegram Bot интеграция
- [ ] PostgreSQL поддержка
- [ ] Redis кеширование
- [ ] Unit тесты (pytest)
- [ ] CI/CD (GitHub Actions)
- [ ] Swagger документация в Swagger Hub

---

**Вопросы или проблемы?** Откройте Issue в репозитории.

**Удачи с хакатоном! 🚀**
