<script setup lang="ts">
import { defineProps } from 'vue';

const props = defineProps<{
  team: any;
}>();
</script>

<template>
  <div class="team-card">
    <h3>{{ props.team.name }}</h3>
    <p v-if="props.team.description" class="description">{{ props.team.description }}</p>
    <div class="meta">
      <span class="status" :class="props.team.status">{{ props.team.status }}</span>
      <span class="members-count">{{ props.team.members?.length || 0 }} участников</span>
    </div>
    <div v-if="props.team.members && props.team.max_team_size" class="capacity-info">
      <span class="capacity-text">{{ props.team.members.length }} / {{ props.team.max_team_size }}</span>
      <span v-if="props.team.members.length >= props.team.max_team_size" class="full-badge">Полная</span>
    </div>
    <router-link :to="`/teams/${props.team.id}`" class="btn-view">Подробнее</router-link>
  </div>
</template>

<style scoped lang="css">
.team-card {
  background: #1e1e2e;
  border-radius: 12px;
  padding: 1.5rem;
  color: #ececec;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.team-card h3 {
  margin: 0;
  color: #4cc5fc;
}

.description {
  color: #b8b8d4;
  font-size: 0.9rem;
  flex: 1;
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
.status.open {
  background: #2a3e2a;
  color: #7fcf7f;
}
.status.closed {
  background: #3e2a2a;
  color: #cf7f7f;
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

.capacity-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  color: #b8b8d4;
  margin-top: 0.5rem;
}

.capacity-text {
  font-weight: 600;
}

.full-badge {
  background: #3e2a2a;
  color: #cf7f7f;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}
</style>

