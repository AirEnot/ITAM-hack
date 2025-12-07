# 🐳 Docker Setup Guide

Полная инструкция по запуску проекта через Docker и Docker Compose.

---

## 📋 Требования

- **Docker** версии 20.10 или выше
- **Docker Compose** версии 2.0 или выше

### Проверка установки

```bash
docker --version
docker-compose --version
```

---

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd ITAM-hack
```

### 2. Настройка переменных окружения (опционально)

Создайте файл `.env` в корне проекта (или используйте значения по умолчанию):

```bash
# .env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_BOT_USERNAME=your_bot_username
SECRET_KEY=your-secret-key-min-32-chars
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=your_secure_password
```

**Примечание:** Если `.env` файл не создан, будут использованы значения по умолчанию из `docker-compose.yml`.

### 3. Запуск через Docker Compose

```bash
# Сборка и запуск контейнеров
docker-compose up --build

# Или в фоновом режиме
docker-compose up -d --build
```

### 4. Проверка работы

После запуска откройте в браузере:

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Документация**: http://localhost:8000/docs

---

## 📁 Структура Docker

```
ITAM-hack/
├── docker-compose.yml          # Основной файл конфигурации
├── .dockerignore               # Исключения для Docker
├── backend/
│   ├── Dockerfile              # Образ для backend
│   ├── .dockerignore          # Исключения для backend
│   └── init_db.py             # Скрипт инициализации БД
└── frontend/
    ├── Dockerfile              # Образ для frontend (multi-stage)
    ├── .dockerignore          # Исключения для frontend
    └── nginx.conf              # Конфигурация Nginx
```

---

## 🔧 Команды Docker Compose

### Основные команды

```bash
# Запуск в фоновом режиме
docker-compose up -d

# Остановка контейнеров
docker-compose down

# Остановка с удалением volumes (БД будет удалена!)
docker-compose down -v

# Просмотр логов
docker-compose logs -f

# Логи только backend
docker-compose logs -f backend

# Логи только frontend
docker-compose logs -f frontend

# Пересборка образов
docker-compose build --no-cache

# Перезапуск сервиса
docker-compose restart backend
docker-compose restart frontend
```

### Работа с контейнерами

```bash
# Войти в контейнер backend
docker-compose exec backend bash

# Войти в контейнер frontend
docker-compose exec frontend sh

# Выполнить команду в контейнере
docker-compose exec backend python add_admin.py
```

---

## 🗄️ База данных

### Расположение

База данных SQLite хранится в:
- **В Docker**: `./backend/data/database.sqlite`
- **Volume**: `backend-db` (Docker volume)

### Инициализация

БД автоматически инициализируется при первом запуске контейнера через скрипт `init_db.py`.

### Создание админа

Админ создается автоматически при первом запуске с данными из переменных окружения:
- Email: `ADMIN_EMAIL` (по умолчанию: `admin@example.com`)
- Password: `ADMIN_PASSWORD` (по умолчанию: `123123`)

### Ручное создание админа

```bash
# Войти в контейнер
docker-compose exec backend bash

# Запустить скрипт
python add_admin.py
```

### Резервное копирование БД

```bash
# Копирование БД из контейнера
docker-compose cp backend:/app/data/database.sqlite ./backup/database_$(date +%Y%m%d_%H%M%S).sqlite

# Восстановление БД
docker-compose cp ./backup/database.sqlite backend:/app/data/database.sqlite
docker-compose restart backend
```

---

## 🌐 Порты и сервисы

| Сервис | Порт | URL |
|--------|------|-----|
| Frontend (Nginx) | 80 | http://localhost |
| Backend (FastAPI) | 8000 | http://localhost:8000 |
| API Docs (Swagger) | 8000 | http://localhost:8000/docs |

### Изменение портов

Отредактируйте `docker-compose.yml`:

```yaml
services:
  frontend:
    ports:
      - "8080:80"  # Изменить 80 на 8080
  backend:
    ports:
      - "8001:8000"  # Изменить 8000 на 8001
```

---

## 🔐 Переменные окружения

### Backend переменные

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DATABASE_URL` | URL базы данных | `sqlite:///./data/database.sqlite` |
| `TELEGRAM_BOT_TOKEN` | Токен Telegram бота | (из config.py) |
| `TELEGRAM_BOT_USERNAME` | Username бота | `bdc_itam_hack_bot` |
| `SECRET_KEY` | Секретный ключ для JWT | (из config.py) |
| `ADMIN_EMAIL` | Email администратора | `admin@example.com` |
| `ADMIN_PASSWORD` | Пароль администратора | `123123` |
| `ALLOWED_ORIGINS` | Разрешенные CORS origins | (список портов) |

### Настройка через .env

Создайте `.env` файл в корне проекта:

```env
TELEGRAM_BOT_TOKEN=your_token_here
SECRET_KEY=your_secret_key_here
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=secure_password
ALLOWED_ORIGINS=http://localhost:80,http://localhost:3000
```

---

## 🛠️ Разработка с Docker

### Hot Reload для Backend

Код backend монтируется как volume, поэтому изменения применяются автоматически. Но для применения изменений в Python коде может потребоваться перезапуск:

```bash
docker-compose restart backend
```

### Hot Reload для Frontend

Для разработки frontend лучше запускать локально:

```bash
cd frontend
npm install
npm run dev
```

Или использовать volume для разработки (требует изменения docker-compose.yml).

### Просмотр логов в реальном времени

```bash
# Все сервисы
docker-compose logs -f

# Только backend
docker-compose logs -f backend

# Только frontend
docker-compose logs -f frontend
```

---

## 🐛 Решение проблем

### Проблема: Порты заняты

**Ошибка:** `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Решение:**
1. Остановите процесс, использующий порт:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   
   # Linux/Mac
   lsof -i :8000
   kill -9 <PID>
   ```
2. Или измените порт в `docker-compose.yml`

### Проблема: БД не инициализируется

**Решение:**
```bash
# Войти в контейнер
docker-compose exec backend bash

# Запустить инициализацию вручную
python init_db.py
```

### Проблема: CORS ошибки

**Решение:**
1. Проверьте `ALLOWED_ORIGINS` в `docker-compose.yml`
2. Добавьте ваш домен в список:
   ```yaml
   ALLOWED_ORIGINS=http://localhost:80,http://your-domain.com
   ```
3. Перезапустите backend:
   ```bash
   docker-compose restart backend
   ```

### Проблема: Frontend не подключается к Backend

**Решение:**
1. Проверьте, что backend запущен:
   ```bash
   docker-compose ps
   ```
2. Проверьте логи:
   ```bash
   docker-compose logs backend
   ```
3. Проверьте конфигурацию nginx в `frontend/nginx.conf`

### Проблема: Контейнеры не запускаются

**Решение:**
```bash
# Очистить все и пересобрать
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Проблема: Изменения не применяются

**Решение:**
```bash
# Пересобрать образы
docker-compose build --no-cache
docker-compose up -d
```

---

## 📦 Production Deployment

### Оптимизация для production

1. **Убрать volume для кода** (использовать только собранные образы):
   ```yaml
   # Закомментировать или удалить:
   # volumes:
   #   - ./backend:/app
   ```

2. **Использовать .env файл** с реальными секретами

3. **Настроить SSL/TLS** через reverse proxy (nginx, traefik)

4. **Использовать PostgreSQL** вместо SQLite:
   ```yaml
   services:
     postgres:
       image: postgres:15-alpine
       environment:
         POSTGRES_DB: hackathon_db
         POSTGRES_USER: hackathon_user
         POSTGRES_PASSWORD: secure_password
       volumes:
         - postgres-data:/var/lib/postgresql/data
   ```

5. **Добавить health checks** (уже добавлены)

---

## 📝 Дополнительные шаги после запуска

### 1. Создание первого админа

Админ создается автоматически при первом запуске. Если нужно создать еще одного:

```bash
docker-compose exec backend python add_admin.py
```

### 2. Настройка Telegram бота

1. Получите токен у [@BotFather](https://t.me/BotFather)
2. Добавьте в `.env` или `docker-compose.yml`:
   ```env
   TELEGRAM_BOT_TOKEN=your_token_here
   TELEGRAM_BOT_USERNAME=your_bot_username
   ```
3. Перезапустите backend:
   ```bash
   docker-compose restart backend
   ```

### 3. Проверка работы API

Откройте http://localhost:8000/docs и протестируйте эндпоинты.

### 4. Проверка работы Frontend

Откройте http://localhost и проверьте, что:
- Страница загружается
- API запросы работают (проверьте Network в DevTools)

---

## 🔄 Обновление проекта

```bash
# Остановить контейнеры
docker-compose down

# Получить последние изменения
git pull

# Пересобрать и запустить
docker-compose up --build -d
```

---

## 🧹 Очистка

```bash
# Остановить и удалить контейнеры
docker-compose down

# Удалить volumes (БД будет удалена!)
docker-compose down -v

# Удалить образы
docker-compose down --rmi all

# Полная очистка (контейнеры + volumes + образы)
docker-compose down -v --rmi all
```

---

## 📚 Полезные ссылки

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue.js Documentation](https://vuejs.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)

---

**Готово!** 🎉 Проект должен быть доступен по адресу http://localhost



