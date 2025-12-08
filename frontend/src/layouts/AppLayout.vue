<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { isUserAuthenticated } from '../utils/auth';
import apiClient from '../utils/api';

const route = useRoute();
const showNav = ref(isUserAuthenticated());
const pendingInvitationsCount = ref(0);
const loadingInvitations = ref(false);

// Обновляем состояние авторизации при изменении маршрута
watch(() => route.path, () => {
  showNav.value = isUserAuthenticated();
  if (showNav.value) {
    loadPendingInvitations();
  }
}, { immediate: true });

// Загружаем количество уведомлений (приглашения + заявки)
async function loadPendingInvitations() {
  if (!isUserAuthenticated()) {
    pendingInvitationsCount.value = 0;
    return;
  }
  
  loadingInvitations.value = true;
  try {
    // Загружаем просмотренные уведомления из localStorage
    let viewedNotifications: number[] = [];
    try {
      const viewed = localStorage.getItem('viewedNotifications');
      if (viewed) {
        viewedNotifications = JSON.parse(viewed);
      }
    } catch (e) {
      // Игнорируем ошибки
    }
    
    // Загружаем приглашения (фильтруем только pending для счетчика)
    const invitationsResponse = await apiClient.get('/api/invitations', {
      params: { status_filter: 'pending' }
    });
    // Считаем только непросмотренные pending приглашения
    let count = invitationsResponse.data?.filter((inv: any) => 
      inv.status === 'pending' && !viewedNotifications.includes(inv.id)
    )?.length || 0;
    
    // Загружаем заявки на вступление в мои команды (для капитана)
    try {
      const applicationsResponse = await apiClient.get('/api/invitations/applications');
      // Считаем только непросмотренные заявки
      const unviewedApplications = applicationsResponse.data?.filter((app: any) => 
        !viewedNotifications.includes(app.id)
      )?.length || 0;
      count += unviewedApplications;
    } catch {
      // Если нет заявок или пользователь не капитан, это нормально
    }
    
    pendingInvitationsCount.value = count;
  } catch {
    pendingInvitationsCount.value = 0;
  } finally {
    loadingInvitations.value = false;
  }
}

// Слушаем события обновления уведомлений
function handleNotificationsUpdated() {
  loadPendingInvitations();
}

// Слушаем события просмотра уведомлений
function handleNotificationsViewed() {
  loadPendingInvitations();
}

onMounted(() => {
  showNav.value = isUserAuthenticated();
  if (showNav.value) {
    loadPendingInvitations();
    // Обновляем каждые 30 секунд
    setInterval(loadPendingInvitations, 30000);
    
    // Слушаем события обновления и просмотра уведомлений
    window.addEventListener('notifications-updated', handleNotificationsUpdated);
    window.addEventListener('notifications-viewed', handleNotificationsViewed);
  }
});
</script>

<template>
  <div class="app-layout">
    <header class="main-header glass-panel">
      <div class="container">
        <router-link to="/" class="logo">ITAM HACK</router-link>
        <nav v-if="showNav" class="main-nav">
          <router-link to="/hackathons">Хакатоны</router-link>
          <router-link to="/team">Мои команды</router-link>
          <router-link to="/invitations" class="invitations-link">
            Уведомления
            <span v-if="pendingInvitationsCount > 0" class="invitations-badge">{{ pendingInvitationsCount }}</span>
          </router-link>
          <router-link to="/profile">Профиль</router-link>
        </nav>
      </div>
    </header>
    <main class="main-content">
      <router-view />
    </main>
    <!-- Мобильная навигация -->
    <nav v-if="showNav" class="mobile-nav glass-liquid">
      <router-link to="/hackathons">
        <span class="nav-emoji">🏆</span>
        <span>Хакатоны</span>
      </router-link>
      <router-link to="/team">
        <span class="nav-emoji">👥</span>
        <span>Мои команды</span>
      </router-link>
      <router-link to="/invitations" class="invitations-link-mobile">
        <span class="nav-emoji">💌</span>
        <span>Уведомления</span>
        <span v-if="pendingInvitationsCount > 0" class="invitations-badge-mobile">{{ pendingInvitationsCount }}</span>
      </router-link>
      <router-link to="/profile">
        <span class="nav-emoji">👤</span>
        <span>Профиль</span>
      </router-link>
      <div class="glass-blob"></div>
      <div class="glass-blob alt"></div>
    </nav>
  </div>
</template>

<style scoped lang="css">
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(160deg, rgba(9, 12, 24, 0.8), rgba(6, 8, 14, 0.9));
  color: var(--text);
}

.main-header {
  background: linear-gradient(140deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.04));
  border-bottom: 1px solid var(--border);
  padding: 0.45rem 0;
  backdrop-filter: blur(var(--blur-strong));
  -webkit-backdrop-filter: blur(var(--blur-strong));
  position: sticky;
  top: 0;
  z-index: 20;
}

.logo {
  font-weight: bold;
  font-size: 1.25rem;
  letter-spacing: 1.8px;
  color: #9ae7ff;
  margin-right: 2rem;
  text-shadow: 0 6px 18px rgba(122, 226, 255, 0.4);
}

.main-header .container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.logo {
  font-size: 1.15rem;
  margin-right: 1rem;
}
.main-nav {
  display: none;
  gap: 1.5rem;
}
.main-nav a {
  color: var(--text);
  text-decoration: none;
  font-size: 1rem;
  position: relative;
  padding: 0.5rem 0.25rem;
  transition: color 0.2s ease;
}
.main-nav a.router-link-active {
  color: #7de2ff;
}
.main-nav a::after {
  content: '';
  display: block;
  width: 0; height: 2px;
  background: linear-gradient(90deg, #7de2ff, #7c63ff);
  transition: width .3s;
  position: absolute;
  left: 0; bottom: -3px;
}
.main-nav a:hover::after,
.main-nav a.router-link-active::after {
  width: 100%;
}

.invitations-link {
  position: relative;
}

.invitations-badge {
  position: absolute;
  top: -8px;
  right: -12px;
  background: #ff6b6b;
  color: #fff;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: bold;
  line-height: 1;
  box-shadow: 0 0 0 4px rgba(255, 107, 107, 0.15);
}

.invitations-link-mobile {
  position: relative;
}

.invitations-badge-mobile {
  position: absolute;
  top: 2px;
  right: 2px;
  background: #ff6b6b;
  color: #fff;
  border-radius: 50%;
  min-width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.65rem;
  font-weight: bold;
  padding: 0 4px;
  line-height: 1;
  box-shadow: 0 0 0 4px rgba(255, 107, 107, 0.18);
}

.main-content {
  flex: 1;
  max-width: 1100px;
  width: 100%;
  margin: 0 auto;
  padding: 1.5rem 1rem 5rem 1rem;
}
.main-footer {
  text-align: center;
  font-size: 0.95rem;
  background: #222237;
  padding: 0.8rem;
  color: #aaa;
  font-weight: 400;
}
.mobile-nav {
  display: flex;
  position: fixed;
  left: 0; bottom: 16px; width: calc(100vw - 24px);
  margin: 0 12px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(22px);
  -webkit-backdrop-filter: blur(22px);
  justify-content: space-around;
  padding: 0.55rem 0.2rem 0.5rem 0.2rem;
  z-index: 31;
  border-radius: 22px;
  box-shadow: 0 25px 70px rgba(0, 0, 0, 0.45), 0 0 0 1px rgba(255, 255, 255, 0.05) inset;
  overflow: hidden;
}
.mobile-nav a {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.1rem;
  font-size: 1.05rem;
  color: var(--text);
  text-decoration: none;
  padding: 0.45rem 0.1rem;
  transition: background 0.18s ease, color 0.18s ease, transform 0.18s ease;
  position: relative;
}
.mobile-nav a span {
  font-size: 0.72rem;
}
.mobile-nav a:hover,
.mobile-nav a.router-link-active {
  background: rgba(255, 255, 255, 0.08);
  color: #7de2ff;
  transform: translateY(-1px);
}
.mobile-nav .nav-emoji {
  filter: drop-shadow(0 4px 10px rgba(0, 0, 0, 0.35));
}
.glass-blob {
  position: absolute;
  width: 140px;
  height: 140px;
  background: radial-gradient(circle, rgba(125, 226, 255, 0.3), rgba(124, 99, 255, 0));
  filter: blur(26px);
  opacity: 0.8;
  right: -20px;
  bottom: -60px;
  pointer-events: none;
  animation: floaty 8s ease-in-out infinite;
}
.glass-blob.alt {
  width: 120px;
  height: 120px;
  left: -30px;
  top: -60px;
  background: radial-gradient(circle, rgba(83, 243, 197, 0.3), rgba(124, 99, 255, 0));
  animation-duration: 9s;
}
@media (min-width: 768px) {
  .main-header .container {
    padding: 0 1.4rem;
  }
  .logo {
    font-size: 1.3rem;
    margin-right: 2rem;
  }
  .main-nav {
    display: flex;
  }
  .mobile-nav {
    display: none;
  }
  .main-content {
    padding: 2rem 1.1rem 2rem 1.1rem;
  }
}
@media (min-width: 1024px) {
  .main-content {
    padding: 2rem 1.5rem;
  }
}
</style>
