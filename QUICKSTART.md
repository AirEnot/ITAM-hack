# 🚀 Быстрый старт проекта ITAM Hack Platform

## Вариант 1: Docker (Рекомендуется) ⭐

### Шаг 1: Установите Docker

- **Windows/Mac**: [Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Linux**: 
  ```bash
  curl -fsSL https://get.docker.com -o get-docker.sh
  sh get-docker.sh
  ```

### Шаг 2: Запустите проект

```bash
# Клонируйте репозиторий (если еще не клонировали)
git clone <repository-url>
cd ITAM-hack

# Запустите все сервисы одной командой
docker-compose up --build
```

### Шаг 3: Откройте в браузере

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Документация**: http://localhost:8000/docs

**Готово!** 🎉

---

## Вариант 2: Локальный запуск (без Docker)

### Backend

```bash
cd backend

# 1. Создайте виртуальное окружение
python -m venv venv

# 2. Активируйте его
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Установите зависимости
pip install -r requirements.txt

# 4. Инициализируйте БД
python -c "from database import init_db; init_db()"

# 5. Создайте админа
python add_admin.py

# 6. Запустите сервер
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# 1. Установите зависимости
npm install

# 2. Запустите dev-сервер
npm run dev
```

Откройте http://localhost:3000 (или порт, указанный в vite.config.ts)

---

## 📝 Что нужно сделать дополнительно

### 1. Настроить Telegram бота (опционально)

1. Создайте бота через [@BotFather](https://t.me/BotFather)
2. Получите токен
3. Добавьте в `.env` или `docker-compose.yml`:
   ```env
   TELEGRAM_BOT_TOKEN=your_token_here
   TELEGRAM_BOT_USERNAME=your_bot_username
   ```

### 2. Изменить пароль админа (рекомендуется)

**В Docker:**
```bash
# Отредактируйте docker-compose.yml или создайте .env файл
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=your_secure_password
```

**Локально:**
```bash
# Отредактируйте backend/config.py или создайте .env в backend/
ADMIN_PASSWORD=your_secure_password
```

### 3. Сгенерировать SECRET_KEY (для production)

```bash
# Linux/Mac
openssl rand -hex 32

# Windows (PowerShell)
[System.Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))

# Python
python -c "import secrets; print(secrets.token_hex(32))"
```

Добавьте в `.env`:
```env
SECRET_KEY=your_generated_secret_key_here
```

### 4. Создать первого хакатон (через админ-панель)

1. Войдите в админ-панель: http://localhost/admin/login
   - Email: `admin@example.com` (или из вашего .env)
   - Password: `123123` (или из вашего .env)
2. Перейдите в "Управление хакатонами"
3. Нажмите "Создать хакатон"
4. Заполните форму и сохраните

---

## 🔍 Проверка работы

### Backend

1. Откройте http://localhost:8000/docs
2. Попробуйте эндпоинт `GET /health` - должен вернуть `{"status": "ok"}`
3. Попробуйте `GET /api/hackathons` (требует авторизации)

### Frontend

1. Откройте http://localhost (или http://localhost:3000 для локального запуска)
2. Нажмите "Вход через Telegram"
3. Следуйте инструкциям для получения кода из бота

---

## 🐛 Решение проблем

### Docker не запускается

```bash
# Проверьте, что Docker запущен
docker ps

# Проверьте логи
docker-compose logs
```

### Порты заняты

Измените порты в `docker-compose.yml`:
```yaml
ports:
  - "8080:80"      # Frontend
  - "8001:8000"    # Backend
```

### БД не создается

```bash
# Войдите в контейнер
docker-compose exec backend bash

# Запустите инициализацию вручную
python init_db.py
```

### CORS ошибки

Добавьте ваш домен в `ALLOWED_ORIGINS` в `docker-compose.yml` или `.env`

---

## 📚 Дополнительная документация

- **Полная инструкция по Docker**: [DOCKER_SETUP.md](./DOCKER_SETUP.md)
- **Backend документация**: [README.md](./README.md)
- **API документация**: http://localhost:8000/docs (после запуска)