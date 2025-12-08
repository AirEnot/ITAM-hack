<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { isUserAuthenticated, isAdminAuthenticated } from '../utils/auth';

const showAuthButtons = ref(true);

function checkAuth() {
  showAuthButtons.value = !isUserAuthenticated() && !isAdminAuthenticated();
}

onMounted(() => {
  checkAuth();
  // Проверяем каждую секунду на случай изменения cookies
  setInterval(checkAuth, 1000);
});
</script>

<template>
  <div class="home-hero glass-panel floating">
    <h1>ITAM Hack Platform</h1>
    <p>Веб-платформа для поиска, создания и управления командами для хакатонов.</p>
    
    <div v-if="showAuthButtons" class="auth-section">
      <router-link to="/auth" class="auth-button">
        <span class="auth-icon">🔐</span>
        <span>Вход через Telegram</span>
      </router-link>
      <router-link to="/admin/login" class="auth-button admin-button">
        <span class="auth-icon">👤</span>
        <span>Вход для админа</span>
      </router-link>
    </div>
    
    <div style="margin-top: 2rem; color: #888; font-size: 0.97rem;">
      code design & development: <b>team BDC</b>
    </div>
  </div>
</template>

<style scoped lang="css">
.home-hero {
  position: relative;
  text-align: center;
  padding: 2.4rem 1.2rem 2.6rem 1.2rem;
  overflow: hidden;
}
.home-hero::after {
  content: '';
  position: absolute;
  width: 480px;
  height: 480px;
  background: radial-gradient(circle, rgba(125, 226, 255, 0.2), transparent 55%);
  top: -280px;
  right: -260px;
  filter: blur(18px);
  pointer-events: none;
  z-index: 0;
}
.home-hero h1 {
  font-size: 2.1rem;
  font-weight: bold;
  letter-spacing: 1.5px;
  margin-bottom: 1rem;
  color: #f5f8ff;
  text-shadow: 0 10px 32px rgba(0, 0, 0, 0.35);
}
.home-hero p {
  color: var(--muted);
  max-width: 520px;
  margin: 0.2rem auto 0 auto;
  font-size: 1rem;
}
.auth-section {
  margin: 2.5rem 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: center;
}

.auth-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 0.9rem 1.9rem;
  background: linear-gradient(135deg, #7de2ff 0%, #7c63ff 45%, #53f3c5 100%);
  color: #fff;
  border-radius: 14px;
  font-size: 1.05rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
  box-shadow: 0 16px 40px rgba(124, 99, 255, 0.25), 0 10px 24px rgba(0, 0, 0, 0.35);
  width: 100%;
  max-width: 400px;
  position: relative;
  overflow: hidden;
  z-index: 1;
}
.auth-button:hover {
  background: linear-gradient(135deg, #8de8ff 0%, #8b79ff 40%, #66f4cf 100%);
  transform: translateY(-2px) scale(1.01);
  box-shadow: 0 20px 50px rgba(124, 99, 255, 0.32), 0 12px 26px rgba(0, 0, 0, 0.38);
  color: #fff;
}
.auth-button.admin-button {
  background: linear-gradient(145deg, #7c63ff 0%, #9a6bff 45%, #ff7de2 100%);
  box-shadow: 0 16px 40px rgba(139, 92, 246, 0.28), 0 10px 24px rgba(0, 0, 0, 0.35);
}
.auth-button.admin-button:hover {
  background: linear-gradient(145deg, #8b79ff 0%, #a478ff 50%, #ff8de6 100%);
  box-shadow: 0 20px 50px rgba(139, 92, 246, 0.35), 0 12px 26px rgba(0, 0, 0, 0.38);
}

.auth-icon {
  font-size: 1.2rem;
}

@media (min-width: 640px) {
  .home-hero {
    padding: 3rem 2rem 2.4rem 2rem;
  }
  .home-hero h1 {
    font-size: 2.4rem;
    letter-spacing: 2.1px;
    margin-bottom: 1.2rem;
  }
}

</style>
