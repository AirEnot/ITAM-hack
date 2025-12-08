import axios, { type AxiosInstance } from 'axios';
import { COOKIE_NAMES } from '../config';

// Используем относительный путь для работы через proxy
// В development Vite proxy обрабатывает /api запросы (см. vite.config.ts)
// В production nginx проксирует /api к backend (см. nginx.conf)
// Переменная VITE_API_BASE_URL может быть установлена для переопределения (обычно пустая строка)
// ВАЖНО: всегда используем пустую строку или относительный путь, чтобы запросы шли через proxy
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_BACKEND_URL ||
  import.meta.env.BACKEND_URL ||
  ''; // Пустая строка = относительные пути через proxy

// Логирование для отладки (только в development)
if (import.meta.env.DEV) {
  console.log('🔧 API Configuration:', {
    VITE_API_BASE_URL: import.meta.env.VITE_API_BASE_URL,
    VITE_BACKEND_URL: import.meta.env.VITE_BACKEND_URL,
    BACKEND_URL: import.meta.env.BACKEND_URL,
    'Final API_BASE_URL': API_BASE_URL || '(empty - using relative paths)',
    'Mode': import.meta.env.MODE,
  });
}

// Создаем базовый экземпляр axios
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Функция для получения токена из cookie
export function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(';').shift() || null;
  return null;
}

// Interceptor для добавления токена авторизации
apiClient.interceptors.request.use(
  (config) => {
    const token = getCookie(COOKIE_NAMES.ACCESS_TOKEN);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor для обработки ошибок
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Обработка сетевых ошибок (нет ответа от сервера)
    if (!error.response) {
      console.error('Network error:', error.message);
      // Если это ошибка сети, пробрасываем её дальше с понятным сообщением
      error.networkError = true;
      error.message = error.message || 'Ошибка сети. Проверьте подключение к интернету.';
    }
    
    if (error.response?.status === 401) {
      // Токен истек или невалиден - очищаем cookies и редиректим на страницу входа
      document.cookie = `${COOKIE_NAMES.ACCESS_TOKEN}=; path=/; max-age=0`;
      document.cookie = `${COOKIE_NAMES.USER_ID}=; path=/; max-age=0`;
      if (window.location.pathname !== '/auth') {
        window.location.href = '/auth';
      }
    }
    return Promise.reject(error);
  }
);

// Создаем отдельный экземпляр для админских запросов
const adminApiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

adminApiClient.interceptors.request.use(
  (config) => {
    const token = getCookie(COOKIE_NAMES.ADMIN_TOKEN);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

adminApiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      document.cookie = 'admin_token=; path=/; max-age=0';
      if (window.location.pathname !== '/admin/login') {
        window.location.href = '/admin/login';
      }
    }
    return Promise.reject(error);
  }
);

// Экспортируем клиенты и базовый URL
export { apiClient, adminApiClient, API_BASE_URL };
export default apiClient;

