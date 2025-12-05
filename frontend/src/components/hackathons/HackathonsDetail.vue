<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import apiClient from '../../utils/api';
import CreateTeamForm from '../teams/CreateTeamForm.vue';
import TeamsList from '../teams/TeamsList.vue';

const props = defineProps<{
  id: string | number; // Параметр из роутера называется 'id'
}>();

const hackathon = ref<any>(null);
const loading = ref(false);
const error = ref('');
const registering = ref(false);
const teamCreated = ref(false);

// Преобразуем id в число (из роутера приходит строка)
const hackathonIdNum = computed(() => {
  const id = typeof props.id === 'string' 
    ? parseInt(props.id, 10) 
    : props.id;
  if (isNaN(id)) {
    throw new Error('Invalid hackathon ID');
  }
  return id;
});

async function loadHackathon() {
  loading.value = true;
  error.value = '';
  try {
    const response = await apiClient.get(`/api/hackathons/${hackathonIdNum.value}`);
    hackathon.value = response.data;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || 'Ошибка';
  } finally {
    loading.value = false;
  }
}

async function register() {
  if (!confirm('Зарегистрироваться на этот хакатон?')) return;
  registering.value = true;
  try {
    await apiClient.post(`/api/hackathons/${hackathonIdNum.value}/register`, {});
    alert('Вы успешно зарегистрированы!');
    loadHackathon();
  } catch (e: any) {
    alert(e?.response?.data?.detail || e?.message || 'Ошибка регистрации');
  } finally {
    registering.value = false;
  }
}

function handleTeamCreated() {
  teamCreated.value = true;
  // Можно обновить список команд, если нужно
}

onMounted(loadHackathon);
</script>

<template>
  <div class="hackathon-detail">
    <div v-if="loading">Загрузка...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="hackathon" class="detail-card">
      <h1>{{ hackathon.name }}</h1>
      <div v-if="hackathon.description" class="description">{{ hackathon.description }}</div>
      <div class="info-grid">
        <div class="info-item">
          <strong>Начало:</strong> {{ new Date(hackathon.start_date).toLocaleString('ru-RU') }}
        </div>
        <div class="info-item">
          <strong>Окончание:</strong> {{ new Date(hackathon.end_date).toLocaleString('ru-RU') }}
        </div>
        <div class="info-item">
          <strong>Статус:</strong> <span class="status" :class="hackathon.status">{{ hackathon.status }}</span>
        </div>
        <div class="info-item">
          <strong>Максимальный размер команды:</strong> {{ hackathon.max_team_size }}
        </div>
      </div>
      <button @click="register" :disabled="registering" class="btn-register">
        {{ registering ? 'Регистрация...' : 'Зарегистрироваться' }}
      </button>
      
      <div v-if="hackathon" class="teams-section">
        <CreateTeamForm 
          :hackathon-id="hackathonIdNum" 
          @team-created="handleTeamCreated"
        />
        <TeamsList :hackathon-id="hackathonIdNum" />
      </div>
    </div>
  </div>
</template>

<style scoped lang="css">
.hackathon-detail {
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

.description {
  color: #b8b8d4;
  line-height: 1.6;
  margin-bottom: 2rem;
}

.info-grid {
  display: grid;
  gap: 1rem;
  margin-bottom: 2rem;
}

.info-item {
  color: #ececec;
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

.btn-register {
  width: 100%;
  padding: 0.8rem;
  background: #0987c7;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
}
.btn-register:disabled {
  background: #555;
  cursor: not-allowed;
}

.error {
  color: #ff6b6b;
  text-align: center;
  padding: 2rem;
}

.teams-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #3a3a4e;
}

@media (min-width: 640px) {
  .detail-card {
    padding: 2rem;
  }
  .detail-card h1 {
    font-size: 2rem;
  }
}
</style>

