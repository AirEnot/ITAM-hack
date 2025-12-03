<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

const props = defineProps<{
  userId?: number;
}>();

const profile = ref<any>(null);
const loading = ref(false);
const error = ref('');

function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(';').shift() || null;
  return null;
}

async function loadProfile() {
  loading.value = true;
  error.value = '';
  try {
    const token = getCookie('access_token');
    if (!token) throw new Error('Нет токена');
    const url = props.userId
      ? `http://localhost:8000/api/users/${props.userId}`
      : 'http://localhost:8000/api/users/me';
    const response = await axios.get(url, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    profile.value = response.data;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || 'Ошибка';
  } finally {
    loading.value = false;
  }
}

onMounted(loadProfile);
</script>

<template>
  <div class="profile-view">
    <div v-if="loading">Загрузка...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="profile" class="profile-card">
      <div class="profile-header">
        <img v-if="profile.avatar_url" :src="profile.avatar_url" alt="Avatar" class="avatar" />
        <div class="profile-info">
          <h2>{{ profile.full_name }}</h2>
          <p v-if="profile.telegram_username">@{{ profile.telegram_username }}</p>
        </div>
      </div>
      <div v-if="profile.bio" class="bio">{{ profile.bio }}</div>
      <div class="profile-details">
        <div class="detail-item">
          <strong>Опыт:</strong> {{ profile.experience_level }}
        </div>
        <div v-if="profile.role_preference" class="detail-item">
          <strong>Роль:</strong> {{ profile.role_preference }}
        </div>
        <div v-if="profile.skills && profile.skills.length > 0" class="skills">
          <strong>Навыки:</strong>
          <div class="skills-list">
            <span v-for="skill in profile.skills" :key="skill" class="skill-tag">{{ skill }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-view {
  max-width: 600px;
  width: 100%;
  margin: 0 auto;
}
.profile-card {
  background: #1e1e2e;
  border-radius: 12px;
  padding: 1.5rem;
  color: #ececec;
}
.profile-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
}
@media (min-width: 640px) {
  .profile-card {
    padding: 2rem;
  }
  .profile-header {
    flex-direction: row;
    text-align: left;
    gap: 1.5rem;
  }
}
.profile-info h2 {
  margin: 0;
  color: #4cc5fc;
}
.bio {
  margin-bottom: 1.5rem;
  color: #b8b8d4;
  line-height: 1.6;
}
.profile-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.detail-item {
  color: #ececec;
}
.skills {
  margin-top: 0.5rem;
}
.skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}
.skill-tag {
  background: #2a2a3e;
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  font-size: 0.9rem;
  color: #4cc5fc;
}
.error {
  color: #ff6b6b;
  text-align: center;
  padding: 2rem;
}
</style>

