<script setup lang="ts">
import { ref, onMounted } from 'vue';

const teams = ref<any[]>([]);
const loading = ref(false);
const error = ref('');

function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(';').shift() || null;
  return null;
}

async function loadMyTeams() {
  loading.value = true;
  error.value = '';
  try {
    const token = getCookie('access_token');
    if (!token) throw new Error('Нет токена');
    // Здесь нужно будет загрузить команды через другой endpoint или через список хакатонов
    // Для MVP показываем сообщение
    teams.value = [];
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || 'Ошибка';
  } finally {
    loading.value = false;
  }
}

onMounted(loadMyTeams);
</script>

<template>
  <div class="my-team">
    <h1>Моя команда</h1>
    <div v-if="loading">Загрузка...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="teams.length === 0" class="empty">
      <p>Вы пока не состоите ни в одной команде.</p>
      <router-link to="/hackathons" class="btn-find">Найти хакатон</router-link>
    </div>
    <div v-else class="teams-list">
      <div v-for="team in teams" :key="team.id" class="team-card">
        <h3>{{ team.name }}</h3>
        <p v-if="team.description">{{ team.description }}</p>
        <a :href="`/teams/${team.id}`" class="btn-view">Подробнее</a>
      </div>
    </div>
  </div>
</template>

<style scoped>
.my-team {
  max-width: 800px;
  margin: 0 auto;
}
.my-team h1 {
  color: #4cc5fc;
  margin-bottom: 2rem;
}
.empty {
  text-align: center;
  padding: 3rem;
  background: #1e1e2e;
  border-radius: 12px;
  color: #b8b8d4;
}
.btn-find {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.8rem 2rem;
  background: #0987c7;
  color: #fff;
  text-decoration: none;
  border-radius: 6px;
}
.error {
  color: #ff6b6b;
  text-align: center;
  padding: 2rem;
}
</style>

