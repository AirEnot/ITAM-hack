<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

const props = defineProps<{
  teamId: number;
}>();

const team = ref<any>(null);
const loading = ref(false);
const error = ref('');

function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(';').shift() || null;
  return null;
}

async function loadTeam() {
  loading.value = true;
  error.value = '';
  try {
    const token = getCookie('access_token');
    if (!token) throw new Error('Нет токена');
    const response = await axios.get(`http://localhost:8000/api/teams/${props.teamId}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    team.value = response.data;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || 'Ошибка';
  } finally {
    loading.value = false;
  }
}

onMounted(loadTeam);
</script>

<template>
  <div class="team-detail">
    <div v-if="loading">Загрузка...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="team" class="detail-card">
      <h1>{{ team.name }}</h1>
      <p v-if="team.description" class="description">{{ team.description }}</p>
      <div class="info">
        <div><strong>Капитан:</strong> {{ team.captain?.full_name }}</div>
        <div><strong>Статус:</strong> <span class="status" :class="team.status">{{ team.status }}</span></div>
        <div><strong>Участников:</strong> {{ team.members?.length || 0 }}</div>
      </div>
      <div v-if="team.members && team.members.length > 0" class="members">
        <h3>Участники:</h3>
        <div class="members-list">
          <div v-for="member in team.members" :key="member.id" class="member-item">
            <strong>{{ member.full_name }}</strong>
            <span v-if="member.role_preference" class="role">{{ member.role_preference }}</span>
            <div v-if="member.skills && member.skills.length > 0" class="skills">
              <span v-for="skill in member.skills" :key="skill" class="skill-tag">{{ skill }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.team-detail {
  max-width: 800px;
  width: 100%;
  margin: 0 auto;
}
.detail-card {
  background: #1e1e2e;
  border-radius: 12px;
  padding: 1.5rem;
  color: #ececec;
}
.detail-card h1 {
  color: #4cc5fc;
  margin-bottom: 1rem;
  font-size: 1.5rem;
}
@media (min-width: 640px) {
  .detail-card {
    padding: 2rem;
  }
  .detail-card h1 {
    font-size: 2rem;
  }
}
.description {
  color: #b8b8d4;
  margin-bottom: 1.5rem;
}
.info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 2rem;
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
.members h3 {
  color: #4cc5fc;
  margin-bottom: 1rem;
}
.members-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.member-item {
  background: #2a2a3e;
  padding: 1rem;
  border-radius: 8px;
}
.member-item .role {
  display: block;
  color: #b8b8d4;
  font-size: 0.9rem;
  margin-top: 0.3rem;
}
.skills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}
.skill-tag {
  background: #1a1a2e;
  padding: 0.3rem 0.6rem;
  border-radius: 4px;
  font-size: 0.85rem;
  color: #4cc5fc;
}
.error {
  color: #ff6b6b;
  text-align: center;
  padding: 2rem;
}
</style>

