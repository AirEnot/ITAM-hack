<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { COOKIE_NAMES } from '../../config';
import { setCookie } from '../../utils/auth';
import { adminApiClient } from '../../utils/api';

const router = useRouter();

const email = ref('');
const password = ref('');
const loading = ref(false);
const error = ref('');

async function loginAdmin() {
  error.value = '';
  loading.value = true;
  try {
    const { data } = await adminApiClient.post('/api/auth/admin/login', {
      email: email.value,
      password: password.value,
    });

    // Сохраняем токен админа в cookie
    setCookie(COOKIE_NAMES.ADMIN_TOKEN, data.access_token, 1);

    // Перенаправляем на админ-дашборд
    router.push('/admin');
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || 'Ошибка входа (email/пароль)';
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="login-box">
    <h2>Вход для администратора</h2>
    <form @submit.prevent="loginAdmin">
      <div>
        <label>Email:</label>
        <input v-model="email" type="email" required />
      </div>
      <div>
        <label>Пароль:</label>
        <input v-model="password" type="password" required />
      </div>
      <button type="submit" :disabled="loading">Войти</button>
      <p v-if="error" style="color: red;"><b>{{ error }}</b></p>
    </form>
  </div>
</template>

<style scoped lang="css">
.login-box {
  max-width: 350px;
  width: 100%;
  margin: 0 auto;
  padding: 1.5rem;
  background: #222;
  border-radius: 10px;
  color: #fff;
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
  background: #0987c7;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
button:disabled { background: #888; cursor: not-allowed; }

@media (min-width: 768px) {
  .login-box {
    padding: 2rem;
  }
}
</style>
