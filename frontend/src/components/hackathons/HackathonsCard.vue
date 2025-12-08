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
  <div class="hackathon-card glass-panel">
    <h3>{{ props.hackathon.name }}</h3>
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

<style scoped lang="css">
.hackathon-card {
  background: linear-gradient(150deg, rgba(255, 255, 255, 0.06), rgba(255, 255, 255, 0.02));
  border-radius: var(--radius-lg);
  padding: 1.3rem;
  color: var(--text);
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  transition: transform 0.25s ease, box-shadow 0.25s ease, border 0.25s ease;
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.hackathon-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-strong);
  border-color: rgba(125, 226, 255, 0.35);
}
.hackathon-card h3 {
  margin: 0;
  color: #f8faff;
  font-size: 1.2rem;
  line-height: 1.3;
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
  font-size: 0.95rem;
  color: var(--muted);
}

.meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
}

/* Стили статусов теперь в глобальном style.css */

.btn-view {
  display: block;
  text-align: center;
  padding: 0.7rem;
  background: linear-gradient(135deg, #7de2ff 0%, #7c63ff 70%);
  color: #04101a;
  text-decoration: none;
  border-radius: 12px;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
  font-weight: 700;
  box-shadow: 0 12px 32px rgba(124, 99, 255, 0.25);
  position: relative;
  z-index: 1;
}
.btn-view:hover {
  background: linear-gradient(135deg, #8de8ff 0%, #8b79ff 70%);
  transform: translateY(-2px);
  box-shadow: 0 16px 40px rgba(124, 99, 255, 0.32);
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
</style>

