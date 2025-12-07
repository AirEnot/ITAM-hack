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
    <header class="main-header">
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
    <nav v-if="showNav" class="mobile-nav">
      <router-link to="/hackathons">🏆<span>Хакатоны</span></router-link>
      <router-link to="/team">👥<span>Мои команды</span></router-link>
      <router-link to="/invitations" class="invitations-link-mobile">
        💌<span>Уведомления</span>
        <span v-if="pendingInvitationsCount > 0" class="invitations-badge-mobile">{{ pendingInvitationsCount }}</span>
      </router-link>
      <router-link to="/profile">👤<span>Профиль</span></router-link>
    </nav>
  </div>
</template>

<style scoped lang="css">
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #18191c;
  color: #ededed;
}

.main-header {
  background: #24244b;
  padding: 0.3rem 0;
}

.logo {
  font-weight: bold;
  font-size: 1.3rem;
  letter-spacing: 1.5px;
  color: #60b7ff;
  margin-right: 2rem;
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
  font-size: 1.1rem;
  margin-right: 1rem;
}
.main-nav {
  display: none;
}
.main-nav a {
  margin-left: 2rem;
  color: #ededed;
  text-decoration: none;
  font-size: 1.05rem;
  position: relative;
}
.main-nav a.router-link-active {
  color: #60b7ff;
}
.main-nav a::after {
  content: '';
  display: block;
  width: 0; height: 2px;
  background: #60b7ff;
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
  left: 0; bottom: 0; width: 100vw;
  background: #23233c;
  border-top: 1px solid #33334c;
  justify-content: space-around;
  padding: 0.3rem 0 0.1rem 0;
  z-index: 31;
}
.mobile-nav a {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  font-size: 1.25rem;
  color: #ededed;
  text-decoration: none;
  padding: 0.3rem 0.1rem;
  transition: background 0.15s;
}
.mobile-nav a span {
  font-size: 0.72rem;
}
.mobile-nav a:hover,
.mobile-nav a.router-link-active {
  background: #252553;
  color: #60b7ff;
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
