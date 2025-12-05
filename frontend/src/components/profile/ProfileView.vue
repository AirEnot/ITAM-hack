<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '../../utils/api';
import { logout } from '../../utils/auth';

const props = defineProps<{
  userId?: number;
}>();

const profile = ref<any>(null);
const loading = ref(false);
const error = ref('');

async function loadProfile() {
  loading.value = true;
  error.value = '';
  try {
    const url = props.userId
      ? `/api/users/${props.userId}`
      : '/api/users/me';
    const response = await apiClient.get(url);
    profile.value = response.data;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || 'Ошибка';
  } finally {
    loading.value = false;
  }
}

function handleLogout() {
  logout();
}

onMounted(loadProfile);
</script>

<template>
  <div class="profile-view">
    <div v-if="loading">Загрузка...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="profile" class="profile-card">
      <div class="profile-header">
        <div class="profile-info">
          <h2>{{ profile.full_name }}</h2>
          <p v-if="profile.telegram_username"> telegram: @{{ profile.telegram_username }}</p>
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
      <div class="profile-actions">
        <router-link to="/profile/edit" class="btn-edit">Редактировать профиль</router-link>
        <button @click="handleLogout" class="btn-logout">Выйти из аккаунта</button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="css">
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

.profile-actions {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #2a2a3e;
}
.btn-edit,
.btn-logout {
  padding: 0.7rem 1.2rem;
  border-radius: 8px;
  font-size: 0.96rem;
  text-decoration: none;
  text-align: center;
  cursor: pointer;
  border: none;
  transition: all 0.15s;
  font-weight: 600;
}
.btn-edit {
  background: #4cc5fc;
  color: #08131a;
}
.btn-edit:hover { opacity: 0.92; }
.btn-logout {
  background: #ff6b6b;
  color: #fff;
}
.btn-logout:hover { opacity: 0.92; }

.error {
  color: #ff6b6b;
  text-align: center;
  padding: 2rem;
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
</style>

