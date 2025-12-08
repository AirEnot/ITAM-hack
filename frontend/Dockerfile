# Frontend Dockerfile
# Multi-stage build для оптимизации размера образа
# Контекст сборки: корень проекта (как на Railway)

# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

# Контекст сборки - корень проекта, поэтому используем frontend/package*.json
COPY frontend/package*.json ./

# Установка зависимостей
RUN npm ci

# Копирование исходного кода
COPY frontend/ .

# Сборка приложения
RUN npm run build

# Stage 2: Production
FROM nginx:alpine

# Копирование собранных файлов из builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Копирование конфигурации nginx
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Открываем порт
EXPOSE 80

# Запуск nginx
CMD ["nginx", "-g", "daemon off;"]



