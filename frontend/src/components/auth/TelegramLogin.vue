<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ROUTES, COOKIE_NAMES } from '../../config';
import apiClient from '../../utils/api';
import { setCookie } from '../../utils/auth';

const router = useRouter();

// Код, который пользователь получает от Telegram-бота
const code = ref('');
const loading = ref(false);
const error = ref('');

// Информация о боте (для ссылки)
const botLink = ref<string | null>(null);
const botUsername = ref<string | null>(null);

async function fetchBotLink() {
  try {
    const { data } = await apiClient.get('/api/auth/telegram/bot-link');
    botLink.value = data.bot_link;
    botUsername.value = data.bot_username;
  } catch {
    // молча игнорируем, просто не покажем ссылку
  }
}

onMounted(() => {
  fetchBotLink();
});

async function loginWithCode() {
  error.value = '';
  if (!code.value.trim()) {
    error.value = 'Введите код из Telegram-бота';
    return;
  }

  loading.value = true;
  try {
    const { data } = await apiClient.post('/api/auth/telegram/verify-code', {
      code: code.value.trim(),
    });

    // Сохраняем токен и id пользователя в cookie
    setCookie(COOKIE_NAMES.ACCESS_TOKEN, data.access_token);
    const userId = data.user?.user_id ?? data.user?.id;
    if (userId) {
      setCookie(COOKIE_NAMES.USER_ID, String(userId));
    }

    // Перенаправляем на дашборд
    router.push('/dashboard');
  } catch (e: any) {
    error.value =
      e?.response?.data?.detail ||
      e?.message ||
      'Произошла ошибка при проверке кода';
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="login-box">
    <h2>Вход через Telegram-бота</h2>

    <p class="description">
      1. Нажмите на кнопку ниже, чтобы открыть Telegram-бота и отправьте команду <b>/start</b>.<br />
      2. Получите от бота одноразовый код.<br />
      3. Вставьте код в поле ниже и нажмите «Войти».
    </p>

    <div v-if="botLink" class="bot-link-wrapper">
      <a :href="botLink" target="_blank" rel="noopener noreferrer" class="bot-link-button">
        Открыть Telegram-бота {{ botUsername ? '@' + botUsername : '' }}
      </a>
    </div>

    <form @submit.prevent="loginWithCode">
      <div>
        <label>Код из Telegram-бота:</label>
        <input v-model="code" type="text" placeholder="Например: 123456" required />
      </div>

      <button type="submit" :disabled="loading">
        {{ loading ? 'Проверяем код...' : 'Войти' }}
      </button>

      <p v-if="error" class="error"><b>{{ error }}</b></p>
    </form>
  </div>
</template>

<style scoped>
.login-box {
  max-width: 380px;
  width: 100%;
  margin: 0 auto;
  padding: 1.8rem;
  background: #222;
  border-radius: 12px;
  color: #fff;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
}

@media (min-width: 768px) {
  .login-box {
    padding: 2.2rem;
  }
}

.description {
  font-size: 0.9rem;
  color: #ccc;
  line-height: 1.4;
  margin-bottom: 1.2rem;
}

.bot-link-wrapper {
  margin-bottom: 1.2rem;
  text-align: center;
}

.bot-link-button {
  display: inline-block;
  padding: 0.6rem 1.2rem;
  border-radius: 999px;
  background: linear-gradient(135deg, #2aabee, #229ed9);
  color: #fff;
  font-weight: 600;
  text-decoration: none;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  box-shadow: 0 6px 18px rgba(34, 158, 217, 0.4);
}

.bot-link-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 24px rgba(34, 158, 217, 0.55);
}

.login-box label {
  display: block;
  margin-top: 1rem;
  margin-bottom: 0.2rem;
}

.login-box input {
  width: 100%;
  padding: 0.5rem 0.6rem;
  border-radius: 6px;
  border: 1px solid #444;
  background: #111;
  color: #fff;
  outline: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
}

.login-box input:focus {
  border-color: #3ca0fa;
  box-shadow: 0 0 0 1px rgba(60, 160, 250, 0.5);
  background: #151515;
}

button {
  width: 100%;
  margin-top: 1.4rem;
  padding: 0.7rem;
  font-size: 1rem;
  font-weight: 600;
  background: #3ca0fa;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s ease, transform 0.1s ease, box-shadow 0.15s ease;
  box-shadow: 0 8px 18px rgba(60, 160, 250, 0.4);
}

button:hover:enabled {
  background: #4bb3ff;
  transform: translateY(-1px);
  box-shadow: 0 10px 24px rgba(60, 160, 250, 0.55);
}

button:disabled {
  background: #888;
  cursor: not-allowed;
  box-shadow: none;
}

.error {
  margin-top: 0.8rem;
  color: #ff6b6b;
}
</style>