# Frontend-Backend Integration Guide

## 🔌 Как фронтенд будет взаимодействовать с вашим бэком

### 1️⃣ АУТЕНТИФИКАЦИЯ УЧАСТНИКА (Telegram)

**Фронт получает `initData` из Telegram Mini App:**

```javascript
// На фронте (React/Vue/etc)
const tg = window.Telegram.WebApp;
const initData = tg.initData;  // Строка вроде: "user_id=123&..."

// Отправляем на бэк
const response = await fetch('http://localhost:8000/api/auth/telegram', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    telegram_id: 123456789,
    telegram_username: "username",
    full_name: "User Name",
    avatar_url: "https://..."
  })
});

const data = await response.json();
// Сохраняем токен в localStorage
localStorage.setItem('access_token', data.access_token);
localStorage.setItem('user_id', data.user_id);
```

### 2️⃣ АУТЕНТИФИКАЦИЯ АДМИНА

**POST /api/admin/login**

```javascript
const response = await fetch('http://localhost:8000/api/admin/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: "admin@example.com",
    password: "password"
  })
});

const data = await response.json();
localStorage.setItem('admin_token', data.access_token);
```

### 3️⃣ ИСПОЛЬЗОВАНИЕ ТОКЕНА В ПОСЛЕДУЮЩИХ ЗАПРОСАХ

**Все запросы содержат Bearer token в заголовке:**

```javascript
const token = localStorage.getItem('access_token');

const response = await fetch('http://localhost:8000/api/users/me', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

---

## 📡 ОСНОВНЫЕ API ENDPOINTS ДЛЯ ФРОНТА

### Участник

| Метод | Endpoint | Описание | Параметры |
|-------|----------|---------|-----------|
| POST | `/api/auth/telegram` | Регистрация/вход | telegram_id, telegram_username, full_name |
| GET | `/api/users/me` | Мой профиль | - |
| PUT | `/api/users/me` | Обновить профиль | full_name, bio, skills, role_preference, experience_level |
| GET | `/api/users/{id}` | Профиль юзера | - |
| GET | `/api/hackathons` | Список хакатонов | - |
| GET | `/api/hackathons/{id}` | Инфо о хакатоне | - |
| POST | `/api/hackathons/{id}/register` | Зарегистрироваться | - |
| POST | `/api/teams` | Создать команду | hackathon_id, name, description |
| GET | `/api/teams/{id}` | Инфо о команде | - |
| GET | `/api/teams/hackathons/{id}` | Команды хакатона | - |
| POST | `/api/teams/{id}/invite` | Пригласить юзера | user_id |
| GET | `/api/invitations` | Мои приглашения | status_filter (optional) |
| POST | `/api/invitations/{id}/accept` | Принять приглашение | accept (boolean) |

### Админ

| Метод | Endpoint | Описание |
|-------|----------|---------|
| POST | `/api/admin/login` | Вход админа |
| GET | `/api/admin/hackathons` | Все хакатоны |
| POST | `/api/admin/hackathons` | Создать хакатон |
| PUT | `/api/admin/hackathons/{id}` | Обновить хакатон |
| GET | `/api/admin/{id}/analytics` | Аналитика |
| GET | `/api/admin/{id}/participants/export` | Экспорт участников CSV |
| GET | `/api/admin/{id}/teams/export` | Экспорт команд CSV |

---

## 🧪 ПРИМЕРЫ ЗАПРОСОВ CURL

### Регистрация участника
```bash
curl -X POST http://localhost:8000/api/auth/telegram \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": 123456789,
    "telegram_username": "testuser",
    "full_name": "Test User",
    "avatar_url": "https://example.com/avatar.jpg"
  }'
```

**Ответ:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user_id": 1
}
```

### Получить свой профиль
```bash
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

curl -X GET http://localhost:8000/api/users/me \
  -H "Authorization: Bearer $TOKEN"
```

### Обновить профиль
```bash
curl -X PUT http://localhost:8000/api/users/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bio": "I love coding",
    "skills": ["Python", "React", "FastAPI"],
    "role_preference": "backend",
    "experience_level": "middle"
  }'
```

### Создать команду
```bash
curl -X POST http://localhost:8000/api/teams \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "hackathon_id": 1,
    "name": "Dream Team",
    "description": "We will build AI solutions"
  }'
```

### Пригласить пользователя
```bash
curl -X POST http://localhost:8000/api/teams/1/invite \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 5}'
```

### Принять приглашение
```bash
curl -X POST http://localhost:8000/api/invitations/1/accept \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"accept": true}'
```

### Админ: Создать хакатон
```bash
ADMIN_TOKEN="admin_token_here"

curl -X POST http://localhost:8000/api/admin/hackathons \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ITAM Hackathon 2025",
    "description": "Banking AI solutions",
    "start_date": "2025-03-01T10:00:00",
    "end_date": "2025-03-02T18:00:00",
    "max_team_size": 5
  }'
```

### Админ: Экспорт участников
```bash
curl -X GET http://localhost:8000/api/admin/1/participants/export \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -o participants.csv
```

---

## ⚠️ ERROR HANDLING

Бэк возвращает HTTP статус коды:

- **200** — OK
- **201** — Created
- **400** — Bad Request (неверные данные)
- **401** — Unauthorized (не авторизован)
- **403** — Forbidden (нет прав)
- **404** — Not Found
- **500** — Internal Server Error

**Пример ошибки:**
```json
{
  "detail": "You are already in a team for this hackathon"
}
```

---

## 🔒 БЕЗОПАСНОСТЬ

1. **Не хранить токен в localStorage** (использовать httpOnly cookies в продакшене)
2. **Всегда использовать HTTPS** в продакшене
3. **Проверять подпись Telegram** на бэке (используется `verify_telegram_signature`)
4. **Не отправлять пароли** в открытом виде
5. **Использовать CORS** только для доверенных доменов

---

## 🐛 ОТЛАДКА

Если что-то не работает:

1. **Откройте DevTools** (F12) → Network
2. **Посмотрите запрос** — правильный ли URL и headers?
3. **Проверьте ответ** — какой статус код?
4. **Посмотрите на бэке логи** — что там пишется?
5. **Откройте /docs** на бэке и проверьте эндпоинты там

### Часто встречаемые ошибки:

```
"detail": "Not authenticated" 
→ Забыли отправить Authorization header

"detail": "Invalid token"
→ Токен истек или неверный

"detail": "CORS policy..."
→ Домен фронта не добавлен в ALLOWED_ORIGINS

"Connection refused"
→ Бэк не запущен (убедитесь что запущен uvicorn)
```

---

## 📚 ПОЛЕЗНЫЕ ССЫЛКИ

- FastAPI docs: https://fastapi.tiangolo.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- JWT: https://jwt.io/
- Telegram Bot API: https://core.telegram.org/bots/api
- Swagger: http://localhost:8000/docs (когда бэк запущен)

---

## 💡 СОВЕТЫ ДЛЯ ФРОНТЕНДЕРА

1. **Используйте fetch или axios** для HTTP запросов
2. **Сохраняйте токен** в localStorage/sessionStorage
3. **Проверяйте токен** перед каждым запросом
4. **Обновляйте UI** основываясь на ответе бэка
5. **Показывайте ошибки** пользователю (из поля `detail`)
6. **Обновляйте список** после создания/удаления элемента
7. **Используйте пагинацию** (skip/limit параметры)

### Пример обновления профиля на React:

```javascript
const updateProfile = async (profileData) => {
  try {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch('http://localhost:8000/api/users/me', {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(profileData)
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }
    
    const updated = await response.json();
    console.log('Profile updated:', updated);
    // Обновить UI
    setProfile(updated);
    
  } catch (error) {
    console.error('Error:', error.message);
    // Показать ошибку пользователю
    alert('Failed to update profile: ' + error.message);
  }
};
```

---

## 🚀 ГОТОВО К ИНТЕГРАЦИИ!

Теперь ваш фронтендер может начать использовать эти эндпоинты для:
- ✅ Регистрации через Telegram
- ✅ Просмотра профиля и других участников
- ✅ Создания/присоединения к командам
- ✅ Управления приглашениями
- ✅ Просмотра хакатонов

А админ может:
- ✅ Управлять хакатонами
- ✅ Смотреть аналитику
- ✅ Экспортировать данные

Успехов! 🎉
