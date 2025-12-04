<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import TeamCard from './TeamCard.vue';

const props = defineProps<{
  hackathonId: number;
}>();

const teams = ref<any[]>([]);
const loading = ref(false);
const error = ref('');

function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(';').shift() || null;
  return null;
}

async function loadTeams() {
  loading.value = true;
  error.value = '';
  try {
    const token = getCookie('access_token');
    if (!token) throw new Error('Нет токена');
    const response = await axios.get(`http://localhost:8000/api/teams/hackathons/${props.hackathonId}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    teams.value = response.data;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || 'Ошибка';
  } finally {
    loading.value = false;
  }
}

onMounted(loadTeams);
</script>

<template>
  <div class="teams-list">
    <h2>Команды</h2>
    <div v-if="loading">Загрузка...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="teams.length === 0" class="empty">Нет команд</div>
    <div v-else class="cards-grid">
      <TeamCard v-for="team in teams" :key="team.id" :team="team" />
    </div>
  </div>
</template>

<style scoped>
.teams-list {
  margin-top: 2rem;
}
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}
.error {
  color: #ff6b6b;
}
.empty {
  color: #888;
  padding: 2rem;
  text-align: center;
}
</style>

