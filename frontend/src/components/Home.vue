<script setup lang="ts">
import { computed } from 'vue';
import { isUserAuthenticated, isAdminAuthenticated } from '../utils/auth';

const showAuthButtons = computed(() => !isUserAuthenticated() && !isAdminAuthenticated());
</script>

<template>
  <div class="home-welcome-text">
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

<style scoped>
.home-welcome-text {
  text-align: center;
  padding: 2rem 1rem 2rem 1rem;
}
.home-welcome-text h1 {
  font-size: 1.8rem;
  font-weight: bold;
  letter-spacing: 1.5px;
  margin-bottom: 1rem;
  color: #70bfff;
}
@media (min-width: 640px) {
  .home-welcome-text {
    padding: 3rem 0 2rem 0;
  }
  .home-welcome-text h1 {
    font-size: 2.1rem;
    letter-spacing: 2.1px;
    margin-bottom: 1.2rem;
  }
}
.home-welcome-text ul {
  margin: 2.2rem auto 1rem auto;
  padding: 0;
  list-style: none;
  max-width: 400px;
}
.home-welcome-text li {
  margin-bottom: 1rem;
}
.home-welcome-text a {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  color: #fff;
  padding: 0.85rem 1.8rem;
  background: linear-gradient(135deg, #3ca0fa 0%, #2d7dd2 100%);
  border-radius: 10px;
  font-size: 1.05rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
  box-shadow: 0 4px 15px rgba(60, 160, 250, 0.3);
  width: 100%;
}
.home-welcome-text a:hover {
  background: linear-gradient(135deg, #4ab0ff 0%, #3d8de2 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(60, 160, 250, 0.4);
  color: #fff;
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
  padding: 0.85rem 1.8rem;
  background: linear-gradient(135deg, #3ca0fa 0%, #2d7dd2 100%);
  color: #fff;
  border-radius: 10px;
  font-size: 1.05rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
  box-shadow: 0 4px 15px rgba(60, 160, 250, 0.3);
  width: 100%;
  max-width: 400px;
}
.auth-button:hover {
  background: linear-gradient(135deg, #4ab0ff 0%, #3d8de2 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(60, 160, 250, 0.4);
  color: #fff;
}
.auth-button.admin-button {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);
}
.auth-button.admin-button:hover {
  background: linear-gradient(135deg, #9d6ff7 0%, #8d4ff0 100%);
  box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4);
}
.auth-icon {
  font-size: 1.2rem;
}
</style>
