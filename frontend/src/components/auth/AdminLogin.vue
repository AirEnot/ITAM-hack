<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const email = ref('');
const password = ref('');
const loading = ref(false);
const error = ref('');

// setCookie с поддержкой дней (локальный хелпер)
function setCookie(name: string, value: string, days: number = 1) {
  const maxAge = 60 * 60 * 24 * days;
  document.cookie = `${name}=${encodeURIComponent(value)}; path=/; max-age=${maxAge}`;
}

async function loginAdmin() {
  error.value = '';
  loading.value = true;
  try {
    const response = await fetch('http://localhost:8000/api/admin/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value, password: password.value })
    });
    if (!response.ok) throw new Error('Ошибка входа (email/пароль)');
    const data = await response.json();
    setCookie('admin_token', data.access_token, 1); // token на 1 день
    // Перенаправляем на админ-дашборд
    router.push('/admin');
  } catch (e: any) {
    error.value = e?.message || 'Ошибка';
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
  background: #0987c7;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
button:disabled { background: #888; cursor: not-allowed; }
</style>
