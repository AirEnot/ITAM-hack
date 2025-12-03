<script setup lang="ts">
import { defineProps } from 'vue';

const props = defineProps<{
  hackathon: any;
}>();

function formatDate(dateStr: string): string {
  const d = new Date(dateStr);
  return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' });
}
</script>

<template>
  <div class="hackathon-card">
    <h3>{{ props.hackathon.name }}</h3>
    <p v-if="props.hackathon.description" class="description">{{ props.hackathon.description }}</p>
    <div class="dates">
      <div>📅 Начало: {{ formatDate(props.hackathon.start_date) }}</div>
      <div>🏁 Окончание: {{ formatDate(props.hackathon.end_date) }}</div>
    </div>
    <div class="meta">
      <span class="status" :class="props.hackathon.status">{{ props.hackathon.status }}</span>
      <span class="team-size">Команда до {{ props.hackathon.max_team_size }} чел.</span>
    </div>
    <router-link :to="`/hackathons/${props.hackathon.id}`" class="btn-view">Подробнее</router-link>
  </div>
</template>

<style scoped>
.hackathon-card {
  background: #1e1e2e;
  border-radius: 12px;
  padding: 1.2rem;
  color: #ececec;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  transition: transform 0.2s;
}
.hackathon-card:hover {
  transform: translateY(-2px);
}
.hackathon-card h3 {
  margin: 0;
  color: #4cc5fc;
  font-size: 1.1rem;
  line-height: 1.3;
}
@media (min-width: 640px) {
  .hackathon-card {
    padding: 1.5rem;
    gap: 1rem;
  }
  .hackathon-card h3 {
    font-size: 1.3rem;
  }
}
.description {
  color: #b8b8d4;
  line-height: 1.5;
  flex: 1;
}
.dates {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #aaa;
}
.meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
}
.status {
  padding: 0.3rem 0.8rem;
  border-radius: 6px;
  text-transform: uppercase;
  font-size: 0.75rem;
}
.status.upcoming {
  background: #2a3e2a;
  color: #7fcf7f;
}
.status.active {
  background: #3e2a2a;
  color: #cf7f7f;
}
.status.finished {
  background: #2a2a3e;
  color: #7f7fcf;
}
.btn-view {
  display: block;
  text-align: center;
  padding: 0.7rem;
  background: #0987c7;
  color: #fff;
  text-decoration: none;
  border-radius: 6px;
  transition: background 0.15s;
}
.btn-view:hover {
  background: #0a9de0;
}
</style>

