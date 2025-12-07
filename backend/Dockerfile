# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов зависимостей
COPY backend/requirements.txt .
COPY backend/ .
# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY . .

# Создание директории для БД
RUN mkdir -p /app/data

# Открываем порт
EXPOSE 8000

# Команда запуска с инициализацией БД
#CMD ["sh", "-c", "python init_db.py && uvicorn main:app --host 0.0.0.0 --port 8000"]
CMD ["sh", "-c", "python init_db.py && python add_admin.py && uvicorn main:app --host 0.0.0.0 --port 8000"]