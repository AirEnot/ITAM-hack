# Backend Dockerfile
# Контекст сборки: корень проекта (как на Railway)
# Для docker-compose контекст также должен быть корнем проекта
FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов зависимостей
# Контекст сборки - корень проекта, поэтому используем backend/requirements.txt
COPY backend/requirements.txt requirements.txt

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
# Контекст сборки - корень проекта, поэтому копируем из backend/
COPY backend/ /app/

# Создание директории для БД
RUN mkdir -p /app/data

# Открываем порт
EXPOSE 8000

# Команда запуска с инициализацией БД
CMD ["sh", "-c", "python init_db.py && python add_admin.py && uvicorn main:app --host 0.0.0.0 --port 8000"]