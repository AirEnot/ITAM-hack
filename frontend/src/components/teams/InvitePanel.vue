<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue';
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

// Состояния для кастомных dropdown
const roleDropdownOpen = ref(false);
const experienceDropdownOpen = ref(false);

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
  roleDropdownOpen.value = false;
  experienceDropdownOpen.value = false;
}

function selectRole(role: string) {
  roleFilter.value = role;
  roleDropdownOpen.value = false;
}

function selectExperience(level: string) {
  experienceFilter.value = level;
  experienceDropdownOpen.value = false;
}

// Закрываем dropdown при клике вне его
function handleClickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement;
  if (!target.closest('.dropdown-wrapper')) {
    roleDropdownOpen.value = false;
    experienceDropdownOpen.value = false;
  }
}

onMounted(() => {
  loadParticipants();
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});

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
      <div class="filter-group dropdown-wrapper">
        <div class="custom-dropdown" @click.stop="roleDropdownOpen = !roleDropdownOpen">
          <span class="dropdown-value">{{ roleFilter || 'Все роли' }}</span>
          <svg class="dropdown-arrow" :class="{ open: roleDropdownOpen }" width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path d="M6 9L1 4h10L6 9z" fill="currentColor"/>
          </svg>
        </div>
        <div v-if="roleDropdownOpen" class="dropdown-menu">
          <div class="dropdown-option" :class="{ active: !roleFilter }" @click="selectRole('')">
            Все роли
          </div>
          <div 
            v-for="role in availableRoles" 
            :key="role" 
            class="dropdown-option" 
            :class="{ active: roleFilter === role }"
            @click="selectRole(role)"
          >
            {{ role }}
          </div>
        </div>
      </div>
      <div class="filter-group dropdown-wrapper">
        <div class="custom-dropdown" @click.stop="experienceDropdownOpen = !experienceDropdownOpen">
          <span class="dropdown-value">{{ experienceFilter || 'Все уровни' }}</span>
          <svg class="dropdown-arrow" :class="{ open: experienceDropdownOpen }" width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path d="M6 9L1 4h10L6 9z" fill="currentColor"/>
          </svg>
        </div>
        <div v-if="experienceDropdownOpen" class="dropdown-menu">
          <div class="dropdown-option" :class="{ active: !experienceFilter }" @click="selectExperience('')">
            Все уровни
          </div>
          <div 
            v-for="level in availableLevels" 
            :key="level" 
            class="dropdown-option" 
            :class="{ active: experienceFilter === level }"
            @click="selectExperience(level)"
          >
            {{ level }}
          </div>
        </div>
      </div>
      <!-- <div class="filter-group">
        <select v-model="skillFilter" class="filter-select">
          <option value="">Все навыки</option>
          <option v-for="skill in availableSkills" :key="skill" :value="skill">{{ skill }}</option>
        </select>
      </div> -->
      <button @click="clearFilters" class="btn-clear-filters btn-ghost">Очистить</button>
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
          class="btn-invite btn-primary"
        >
          {{ inviting === participant.id ? 'Отправка...' : 'Пригласить' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="css">
.invite-panel {
  margin-top: 2rem;
  padding: 1.6rem;
  border-radius: var(--radius-lg);
  background: var(--glass);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-soft);
  backdrop-filter: blur(var(--blur-soft));
  -webkit-backdrop-filter: blur(var(--blur-soft));
  position: relative;
  overflow: visible;
}
.invite-panel h3 {
  color: #f8faff;
  margin-bottom: 1.2rem;
  font-size: 1.2rem;
}

.filters {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  margin-bottom: 1.5rem;
  padding: 1.2rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: var(--radius-sm);
  border: 1px solid rgba(255, 255, 255, 0.08);
  overflow: visible;
  position: relative;
}

.filter-group {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

@media (min-width: 640px) {
  .filter-group {
    min-width: 140px;
  }
  
  .filter-group:first-child {
    min-width: 0;
  }
}

.filter-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  color: var(--text);
  font-size: 0.95rem;
  font-family: inherit;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.filter-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.filter-input:focus {
  outline: none;
  border-color: rgba(125, 226, 255, 0.5);
  background: rgba(255, 255, 255, 0.12);
  box-shadow: 0 6px 20px rgba(125, 226, 255, 0.2), 0 0 0 3px rgba(125, 226, 255, 0.1);
}

.dropdown-wrapper {
  position: relative;
  z-index: 10;
}

.custom-dropdown {
  width: 100%;
  padding: 0.75rem 1rem;
  padding-right: 2.5rem;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  color: var(--text);
  font-size: 0.95rem;
  font-family: inherit;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
}

.custom-dropdown:hover {
  border-color: rgba(125, 226, 255, 0.4);
  background: rgba(255, 255, 255, 0.1);
}

.dropdown-value {
  flex: 1;
  color: var(--text);
}

.dropdown-arrow {
  position: absolute;
  right: 0.75rem;
  color: rgba(255, 255, 255, 0.7);
  transition: transform 0.2s ease;
  pointer-events: none;
}

.dropdown-arrow.open {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 0.5rem);
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(5, 6, 12, 0.85);
  backdrop-filter: blur(40px);
  -webkit-backdrop-filter: blur(40px);
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 14px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.08) inset;
  overflow-y: auto !important;
  overflow-x: hidden !important;
  max-height: 120px !important;
  animation: dropdownFadeIn 0.2s ease;
  min-width: 100%;
  /* Для Firefox */
  scrollbar-width: thin !important;
  scrollbar-color: rgba(125, 226, 255, 0.6) rgba(255, 255, 255, 0.1) !important;
}

/* Стилизация скроллбара для dropdown (WebKit) */
.dropdown-menu::-webkit-scrollbar {
  width: 8px !important;
  display: block !important;
}

.dropdown-menu::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1) !important;
  border-radius: 10px !important;
  margin: 4px 0 !important;
}

.dropdown-menu::-webkit-scrollbar-thumb {
  background: rgba(125, 226, 255, 0.6) !important;
  border-radius: 10px !important;
  transition: background 0.2s ease !important;
  border: 1px solid rgba(125, 226, 255, 0.2) !important;
}

.dropdown-menu::-webkit-scrollbar-thumb:hover {
  background: rgba(125, 226, 255, 0.8) !important;
  border-color: rgba(125, 226, 255, 0.4) !important;
}

@keyframes dropdownFadeIn {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-option {
  padding: 0.75rem 1rem;
  color: var(--text);
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.15s ease;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.dropdown-option:last-child {
  border-bottom: none;
}

.dropdown-option:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #7de2ff;
}

.dropdown-option.active {
  background: linear-gradient(135deg, rgba(125, 226, 255, 0.2), rgba(124, 99, 255, 0.15));
  color: #7de2ff;
  font-weight: 600;
}

.btn-clear-filters {
  padding: 0.75rem 1.2rem;
  border-radius: 12px;
  font-size: 0.9rem;
  white-space: nowrap;
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
  background: linear-gradient(140deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02));
  padding: 1rem;
  border-radius: var(--radius-lg);
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(var(--blur-soft));
  -webkit-backdrop-filter: blur(var(--blur-soft));
}

.participant-info {
  flex: 1;
  width: 100%;
}
.participant-info strong {
  color: var(--text);
  display: block;
  margin-bottom: 0.3rem;
}
.participant-info .role {
  display: block;
  color: var(--muted);
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
  background: rgba(255, 255, 255, 0.06);
  padding: 0.3rem 0.6rem;
  border-radius: 6px;
  font-size: 0.85rem;
  color: #9ae7ff;
  border: 1px solid rgba(154, 231, 255, 0.2);
}

.btn-invite {
  width: 100%;
  padding: 0.7rem 1.2rem;
  border-radius: 12px;
  font-size: 0.95rem;
}
.btn-invite:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
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

