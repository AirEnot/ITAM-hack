<script setup lang="ts">
import { ref, onMounted, defineProps, defineEmits } from 'vue';
import { adminApiClient } from '../../utils/api';

const props = defineProps<{
  mode: 'create' | 'edit';
  hackathonId?: number;
}>();

const emit = defineEmits<{
  saved: [];
  cancelled: [];
}>();

const form = ref({
  name: '',
  description: '',
  start_date: '',
  end_date: '',
  max_team_size: 5,
  status: 'upcoming'
});

const loading = ref(false);
const error = ref('');
const validationErrors = ref<Record<string, string>>({});

function formatDateTimeForInput(dateStr: string): string {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  return `${year}-${month}-${day}T${hours}:${minutes}`;
}

async function loadHackathon() {
  if (props.mode !== 'edit' || !props.hackathonId) return;
  loading.value = true;
  error.value = '';
  try {
    const response = await adminApiClient.get('/api/admin/hackathons');
    const hackathon = response.data.find((h: any) => h.id === props.hackathonId);
    if (!hackathon) throw new Error('Хакатон не найден');
    form.value.name = hackathon.name;
    form.value.description = hackathon.description || '';
    form.value.start_date = formatDateTimeForInput(hackathon.start_date);
    form.value.end_date = formatDateTimeForInput(hackathon.end_date);
    form.value.max_team_size = hackathon.max_team_size;
    form.value.status = hackathon.status;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || 'Ошибка загрузки';
  } finally {
    loading.value = false;
  }
}

function validate(): boolean {
  validationErrors.value = {};
  if (!form.value.name.trim()) {
    validationErrors.value.name = 'Название обязательно';
  }
  if (!form.value.start_date) {
    validationErrors.value.start_date = 'Дата начала обязательна';
  }
  if (!form.value.end_date) {
    validationErrors.value.end_date = 'Дата окончания обязательна';
  }
  if (form.value.start_date && form.value.end_date) {
    if (new Date(form.value.end_date) <= new Date(form.value.start_date)) {
      validationErrors.value.end_date = 'Дата окончания должна быть позже даты начала';
    }
  }
  if (form.value.max_team_size < 1) {
    validationErrors.value.max_team_size = 'Размер команды должен быть >= 1';
  }
  return Object.keys(validationErrors.value).length === 0;
}

async function save() {
  if (!validate()) return;
  loading.value = true;
  error.value = '';
  try {
    const url = props.mode === 'create'
      ? '/api/hackathons'
      : `/api/hackathons/${props.hackathonId}`;
    const payload: any = {
      name: form.value.name,
      description: form.value.description || null,
      start_date: new Date(form.value.start_date).toISOString(),
      end_date: new Date(form.value.end_date).toISOString(),
      max_team_size: form.value.max_team_size,
    };
    if (props.mode === 'edit') {
      payload.status = form.value.status;
    }
    if (props.mode === 'create') {
      await adminApiClient.post(url, payload);
    } else {
      await adminApiClient.put(url, payload);
    }
    emit('saved');
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || 'Ошибка сохранения';
  } finally {
    loading.value = false;
  }
}

function cancel() {
  emit('cancelled');
}

onMounted(() => {
  if (props.mode === 'edit') {
    loadHackathon();
  }
});
</script>

<template>
  <div class="hackathon-edit-form">
    <h2>{{ props.mode === 'create' ? 'Создать хакатон' : 'Редактировать хакатон' }}</h2>
    <div v-if="loading && props.mode === 'edit'" class="loading">Загрузка...</div>
    <form v-else @submit.prevent="save">
      <div class="form-group">
        <label>Название *</label>
        <input v-model="form.name" type="text" required />
        <span v-if="validationErrors.name" class="error-text">{{ validationErrors.name }}</span>
      </div>
      <div class="form-group">
        <label>Описание</label>
        <textarea v-model="form.description" rows="4"></textarea>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>Дата начала *</label>
          <input v-model="form.start_date" type="datetime-local" required />
          <span v-if="validationErrors.start_date" class="error-text">{{ validationErrors.start_date }}</span>
        </div>
        <div class="form-group">
          <label>Дата окончания *</label>
          <input v-model="form.end_date" type="datetime-local" required />
          <span v-if="validationErrors.end_date" class="error-text">{{ validationErrors.end_date }}</span>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>Максимальный размер команды</label>
          <input v-model.number="form.max_team_size" type="number" min="1" />
          <span v-if="validationErrors.max_team_size" class="error-text">{{ validationErrors.max_team_size }}</span>
        </div>
        <div v-if="props.mode === 'edit'" class="form-group">
          <label>Статус</label>
          <select v-model="form.status">
            <option value="upcoming">Предстоящий</option>
            <option value="active">Активный</option>
            <option value="finished">Завершен</option>
          </select>
        </div>
      </div>
      <div v-if="error" class="error-message">{{ error }}</div>
      <div class="form-actions">
        <button type="submit" :disabled="loading" class="btn-primary">Сохранить</button>
        <button type="button" @click="cancel" class="btn-secondary">Отмена</button>
      </div>
    </form>
  </div>
</template>

<style scoped lang="css">
.hackathon-edit-form {
  max-width: 800px;
  width: 100%;
  margin: 1rem auto;
  padding: 1.5rem;
  background: #1e1e2e;
  border-radius: 12px;
  color: #ececec;
}
.hackathon-edit-form h2 {
  color: #4cc5fc;
  margin-bottom: 1.8rem;
}

.form-group {
  margin-bottom: 1.5rem;
}
.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
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
.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #4cc5fc;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.error-text {
  display: block;
  color: #ff6b6b;
  font-size: 0.9rem;
  margin-top: 0.3rem;
}

.error-message {
  background: #4a1a1a;
  color: #ff6b6b;
  padding: 0.8rem;
  border-radius: 6px;
  margin-bottom: 1rem;
}

.form-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 2rem;
}

.btn-primary,
.btn-secondary {
  padding: 0.7rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.15s;
  width: 100%;
}

.btn-primary {
  background: #0987c7;
  color: #fff;
}
.btn-primary:hover:not(:disabled) {
  background: #0a9de0;
}
.btn-primary:disabled {
  background: #555;
  cursor: not-allowed;
}

.btn-secondary {
  background: #3a3a4e;
  color: #ececec;
}
.btn-secondary:hover {
  background: #4a4a5e;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #70bfff;
}

@media (min-width: 768px) {
  .hackathon-edit-form {
    margin: 2rem auto;
    padding: 2rem;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}

@media (min-width: 640px) {
  .form-actions {
    flex-direction: row;
  }

  .btn-primary,
  .btn-secondary {
    width: auto;
    padding: 0.7rem 1.8rem;
  }
}
</style>

