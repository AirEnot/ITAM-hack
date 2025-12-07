<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import apiClient from '../../utils/api';

const props = defineProps<{
  teamId: number | string;
  hackathonId: number | string;
}>();

const emit = defineEmits<{
  (e: 'invite-sent'): void;
}>();

const participants = ref<any[]>([]);
const loading = ref(false);
const error = ref('');
const inviting = ref<number | null>(null);

// Фильтры
const searchQuery = ref('');
const roleFilter = ref('');
const experienceFilter = ref('');
const skillFilter = ref('');

const availableRoles = ['frontend', 'backend', 'fullstack', 'designer', 'product manager'];
const availableLevels = ['junior', 'middle', 'senior'];
const availableSkills = ref<string[]>([]);

async function loadParticipants() {
  loading.value = true;
  error.value = '';
  try {
    const hackathonId = typeof props.hackathonId === 'string' 
      ? parseInt(props.hackathonId, 10) 
      : props.hackathonId;
    
    const params: any = {};
    if (searchQuery.value) params.search = searchQuery.value;
    if (roleFilter.value) params.role_preference = roleFilter.value;
    if (experienceFilter.value) params.experience_level = experienceFilter.value;
    if (skillFilter.value) params.skill = skillFilter.value;
    
    const response = await apiClient.get(`/api/users/hackathons/${hackathonId}/participants`, { params });
    participants.value = response.data;
    
    // Собираем уникальные навыки для фильтра
    const skillsSet = new Set<string>();
    response.data.forEach((p: any) => {
      if (p.skills && Array.isArray(p.skills)) {
        p.skills.forEach((s: string) => skillsSet.add(s));
      }
    });
    availableSkills.value = Array.from(skillsSet).sort();
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || 'Ошибка';
  } finally {
    loading.value = false;
  }
}

// Debounce функция
let debounceTimer: ReturnType<typeof setTimeout> | null = null;

// Перезагружаем при изменении фильтров с debounce
watch([searchQuery, roleFilter, experienceFilter, skillFilter], () => {
  if (debounceTimer) {
    clearTimeout(debounceTimer);
  }
  debounceTimer = setTimeout(() => {
    loadParticipants();
  }, 300);
});

function clearFilters() {
  searchQuery.value = '';
  roleFilter.value = '';
  experienceFilter.value = '';
  skillFilter.value = '';
}

async function inviteUser(userId: number) {
  if (!confirm('Отправить приглашение этому пользователю?')) return;
  inviting.value = userId;
  try {
    const teamId = typeof props.teamId === 'string' 
      ? parseInt(props.teamId, 10) 
      : props.teamId;
    await apiClient.post(`/api/teams/${teamId}/invite`, null, {
      params: { user_id: userId },
    });
    alert('Приглашение отправлено!');
    emit('invite-sent');
  } catch (e: any) {
    alert(e?.response?.data?.detail || e?.message || 'Ошибка');
  } finally {
    inviting.value = null;
  }
}

onMounted(loadParticipants);
</script>

<template>
  <div class="invite-panel">
    <h3>Пригласить участников</h3>
    
    <!-- Фильтры -->
    <div class="filters">
      <div class="filter-group">
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Поиск по имени..." 
          class="filter-input"
        />
      </div>
      <div class="filter-group">
        <select v-model="roleFilter" class="filter-select">
          <option value="">Все роли</option>
          <option v-for="role in availableRoles" :key="role" :value="role">{{ role }}</option>
        </select>
      </div>
      <div class="filter-group">
        <select v-model="experienceFilter" class="filter-select">
          <option value="">Все уровни</option>
          <option v-for="level in availableLevels" :key="level" :value="level">{{ level }}</option>
        </select>
      </div>
      <!-- <div class="filter-group">
        <select v-model="skillFilter" class="filter-select">
          <option value="">Все навыки</option>
          <option v-for="skill in availableSkills" :key="skill" :value="skill">{{ skill }}</option>
        </select>
      </div> -->
      <button @click="clearFilters" class="btn-clear-filters">Очистить</button>
    </div>
    
    <div v-if="loading">Загрузка...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="participants.length === 0" class="empty">Нет доступных участников</div>
    <div v-else class="participants-list">
      <div v-for="participant in participants" :key="participant.id" class="participant-card">
        <div class="participant-info">
          <strong>{{ participant.full_name }}</strong>
          <span v-if="participant.role_preference" class="role">{{ participant.role_preference }}</span>
          <div v-if="participant.skills && participant.skills.length > 0" class="skills">
            <span v-for="skill in participant.skills" :key="skill" class="skill-tag">{{ skill }}</span>
          </div>
        </div>
        <button
          @click="inviteUser(participant.id)"
          :disabled="inviting === participant.id"
          class="btn-invite"
        >
          {{ inviting === participant.id ? 'Отправка...' : 'Пригласить' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="css">
.invite-panel {
  background: #1e1e2e;
  border-radius: 12px;
  padding: 1.5rem;
  margin-top: 2rem;
}
.invite-panel h3 {
  color: #4cc5fc;
  margin-bottom: 1rem;
}

.filters {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #2a2a3e;
  border-radius: 8px;
}

.filter-group {
  display: flex;
  flex-direction: column;
}

.filter-input,
.filter-select {
  width: 100%;
  padding: 0.6rem;
  border-radius: 6px;
  border: 1px solid #444;
  background: #1a1a2e;
  color: #fff;
  font-size: 0.9rem;
}

.filter-input:focus,
.filter-select:focus {
  outline: none;
  border-color: #4cc5fc;
}

.btn-clear-filters {
  padding: 0.6rem 1rem;
  background: #555;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-clear-filters:hover {
  background: #666;
}

@media (min-width: 640px) {
  .filters {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr auto;
    gap: 0.8rem;
    align-items: end;
  }
  
  .filter-group {
    display: flex;
    flex-direction: column;
  }
}

.participants-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.participant-card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: #2a2a3e;
  padding: 1rem;
  border-radius: 8px;
}

.participant-info {
  flex: 1;
  width: 100%;
}
.participant-info .role {
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

.btn-invite {
  width: 100%;
  padding: 0.6rem 1.2rem;
  background: #0987c7;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.btn-invite:disabled {
  background: #555;
  cursor: not-allowed;
}

.error {
  color: #ff6b6b;
}

.empty {
  color: #888;
  text-align: center;
  padding: 2rem;
}

@media (min-width: 640px) {
  .participant-card {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    gap: 0;
  }
  .btn-invite {
    width: auto;
  }
}
</style>

