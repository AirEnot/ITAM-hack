<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '../../utils/api';

const form = ref({
  full_name: '',
  bio: '',
  skills: [] as string[],
  role_preference: '',
  experience_level: 'junior',
});

const newSkill = ref('');
const loading = ref(false);
const saving = ref(false);
const error = ref('');

async function loadProfile() {
  loading.value = true;
  error.value = '';
  try {
    const response = await apiClient.get('/api/users/me');
    const profile = response.data;
    form.value.full_name = profile.full_name;
    form.value.bio = profile.bio || '';
    form.value.skills = profile.skills || [];
    form.value.role_preference = profile.role_preference || '';
    form.value.experience_level = profile.experience_level;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || 'Ошибка';
  } finally {
    loading.value = false;
  }
}

function addSkill() {
  if (newSkill.value.trim() && !form.value.skills.includes(newSkill.value.trim())) {
    form.value.skills.push(newSkill.value.trim());
    newSkill.value = '';
  }
}

function removeSkill(skill: string) {
  form.value.skills = form.value.skills.filter(s => s !== skill);
}

async function save() {
  saving.value = true;
  error.value = '';
  try {
    await apiClient.put('/api/users/me', form.value);
    alert('Профиль обновлен!');
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || 'Ошибка';
  } finally {
    saving.value = false;
  }
}

onMounted(loadProfile);
</script>

<template>
  <div class="profile-edit">
    <h2>Редактировать профиль</h2>
    <div v-if="loading">Загрузка...</div>
    <form v-else @submit.prevent="save">
      <div class="form-group">
        <label>Имя *</label>
        <input v-model="form.full_name" type="text" required />
      </div>
      <div class="form-group">
        <label>О себе</label>
        <textarea v-model="form.bio" rows="4"></textarea>
      </div>
      <div class="form-group">
        <label>Опыт</label>
        <select v-model="form.experience_level">
          <option value="junior">Junior</option>
          <option value="middle">Middle</option>
          <option value="senior">Senior</option>
        </select>
      </div>
      <div class="form-group">
        <label>Роль</label>
        <select v-model="form.role_preference">
          <option value="">Не указано</option>
          <option value="frontend">Frontend</option>
          <option value="backend">Backend</option>
          <option value="fullstack">Fullstack</option>
          <option value="designer">Designer</option>
        </select>
      </div>
      <div class="form-group">
        <label>Навыки</label>
        <div class="skills-input">
          <input v-model="newSkill" type="text" placeholder="Добавить навык" @keyup.enter.prevent="addSkill" />
          <button type="button" @click="addSkill">Добавить</button>
        </div>
        <div class="skills-list">
          <span v-for="skill in form.skills" :key="skill" class="skill-tag">
            {{ skill }}
            <button type="button" @click="removeSkill(skill)" class="remove-skill">×</button>
          </span>
        </div>
      </div>
      <div v-if="error" class="error">{{ error }}</div>
      <button type="submit" :disabled="saving" class="btn-save">Сохранить</button>
    </form>
  </div>
</template>

<style scoped lang="css">
.profile-edit {
  max-width: 600px;
  width: 100%;
  margin: 0 auto;
  background: #1e1e2e;
  border-radius: 12px;
  padding: 1.5rem;
  color: #ececec;
}
.profile-edit h2 {
  color: #4cc5fc;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}
.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #b8b8d4;
}
.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.7rem;
  background: #2a2a3e;
  border: 1px solid #3a3a4e;
  border-radius: 6px;
  color: #ececec;
  font-size: 1rem;
}

.skills-input {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}
.skills-input input {
  flex: 1;
}
.skills-input button {
  padding: 0.7rem 1rem;
  background: #0987c7;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  white-space: nowrap;
}

@media (min-width: 640px) {
  .profile-edit {
    padding: 2rem;
  }

  .skills-input {
    flex-direction: row;
  }
} 
.skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.skill-tag {
  background: #2a2a3e;
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.remove-skill {
  background: transparent;
  border: none;
  color: #ff6b6b;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-save {
  width: 100%;
  padding: 0.8rem;
  background: #0987c7;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  margin-top: 1rem;
}
.btn-save:disabled {
  background: #555;
  cursor: not-allowed;
}

.error {
  color: #ff6b6b;
  margin-bottom: 1rem;
}


</style>

