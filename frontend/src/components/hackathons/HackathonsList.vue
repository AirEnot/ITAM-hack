<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '../../utils/api';
import HackathonsCard from './HackathonsCard.vue';

const hackathons = ref<any[]>([]);
const loading = ref(false);
const error = ref('');

async function loadHackathons() {
  loading.value = true;
  error.value = '';
  try {
    const response = await apiClient.get('/api/hackathons');
    hackathons.value = response.data;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || 'Ошибка';
  } finally {
    loading.value = false;
  }
}

onMounted(loadHackathons);
</script>

<template>
  <div class="hackathons-list">
    <h1>Хакатоны</h1>
    <div v-if="loading">Загрузка...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="hackathons.length === 0" class="empty">Нет доступных хакатонов</div>
    <div v-else class="cards-grid">
      <HackathonsCard v-for="hackathon in hackathons" :key="hackathon.id" :hackathon="hackathon" />
    </div>
  </div>
</template>

<style scoped lang="css">
.hackathons-list {
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}
.hackathons-list h1 {
  color: #4cc5fc;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.cards-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

.error {
  color: #ff6b6b;
  text-align: center;
  padding: 1.5rem;
  font-size: 0.9rem;
}

.empty {
  text-align: center;
  color: #888;
  padding: 2rem 1rem;
}

@media (min-width: 1024px) {
  .cards-grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }
}

@media (min-width: 640px) {
  .hackathons-list h1 {
    font-size: 2rem;
    margin-bottom: 2rem;
  }
  .cards-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.5rem;
  }
  .error {
    padding: 2rem;
  }
  .empty {
    padding: 3rem;
  }
}
</style>

