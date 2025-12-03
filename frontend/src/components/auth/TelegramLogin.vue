<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// Для MVP-логина через Telegram:
const telegram_id = ref('');
const telegram_username = ref('');
const full_name = ref('');
const avatar_url = ref('');
const loading = ref(false);
const error = ref('');

function setCookie(name: string, value: string, days: number = 7) {
  const maxAge = 60 * 60 * 24 * days;
  document.cookie = `${name}=${encodeURIComponent(value)}; path=/; max-age=${maxAge}`;
}

async function loginWithTelegram() {
  error.value = '';
  loading.value = true;
  try {
    const response = await fetch('http://localhost:8000/api/auth/telegram', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        telegram_id: +telegram_id.value, // as number
        telegram_username: telegram_username.value,
        full_name: full_name.value,
        avatar_url: avatar_url.value,
      })
    });
    if (!response.ok) throw new Error('Ошибка авторизации');
    const data = await response.json();
    // Сохраняем токен в cookie
    setCookie('access_token', data.access_token);
    setCookie('user_id', data.user_id);
    // Перенаправляем на страницу хакатонов
    router.push('/hackathons');
  } catch (e: any) {
    error.value = e?.message || 'Произошла ошибка';
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="login-box">
    <h2>Вход через Telegram</h2>
    <form @submit.prevent="loginWithTelegram">
      <div>
        <label>Telegram ID:</label>
        <input v-model="telegram_id" type="text" required />
      </div>
      <div>
        <label>Username:</label>
        <input v-model="telegram_username" type="text" />
      </div>
      <div>
        <label>Имя:</label>
        <input v-model="full_name" type="text" required />
      </div>
      <div>
        <label>URL аватарки (опц.):</label>
        <input v-model="avatar_url" type="text" />
      </div>
      <button type="submit" :disabled="loading">Войти</button>
      <p v-if="error" style="color: red;"><b>{{ error }}</b></p>
    </form>
  </div>
</template>

<style scoped>
.login-box {
  max-width: 350px;
  width: 100%;
  margin: 0 auto;
  padding: 1.5rem;
  background: #222;
  border-radius: 10px;
  color: #fff;
}
@media (min-width: 768px) {
  .login-box {
    padding: 2rem;
  }
}
.login-box label {
  display: block;
  margin-top: 1rem;
}
.login-box input {
  width: 100%;
  padding: 0.4rem;
  margin-top: 0.2rem;
  border-radius: 3px;
  border: 1px solid #444;
  background: #111;
  color: #fff;
}
button {
  width: 100%;
  margin-top: 1.2rem;
  padding: 0.6rem;
  font-size: 1rem;
  background: #3ca0fa;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
button:disabled { background: #888; cursor: not-allowed; }
</style>
