<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

const hackathons = ref<any[]>([]);
const loading = ref(true);
const error = ref('');
const analytics = ref<any|null>(null);
const analyticsLoading = ref(false);
const analyticsError = ref('');

function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(';').shift() || null;
  return null;
}

async function fetchHackathons() {
  loading.value = true;
  error.value = '';
  try {
    const token = getCookie('admin_token');
    if (!token) throw new Error('Нет admin_token. Войдите как администратор!');
    const response = await axios.get('http://localhost:8000/api/admin/hackathons', {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    hackathons.value = response.data;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || 'Ошибка';
  } finally {
    loading.value = false;
  }
}

async function fetchAnalytics(hackathonId: number) {
  analytics.value = null;
  analyticsLoading.value = true;
  analyticsError.value = '';
  try {
    const token = getCookie('admin_token');
    if (!token) throw new Error('Нет admin_token');
    const response = await axios.get(`http://localhost:8000/api/admin/${hackathonId}/analytics`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    analytics.value = response.data;
  } catch (e: any) {
    analyticsError.value = e?.response?.data?.detail || e?.message || 'Ошибка';
  } finally {
    analyticsLoading.value = false;
  }
}

async function downloadCSV(url: string, filename: string) {
  const token = getCookie('admin_token');
  if (!token) {
    alert('Нет admin_token!');
    return;
  }
  try {
    const response = await axios.get(url, {
      responseType: 'blob',
      headers: { 'Authorization': `Bearer ${token}` },
    });
    const href = URL.createObjectURL(response.data);
    const link = document.createElement('a');
    link.href = href;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(href);
  } catch (e: any) {
    alert('Ошибка скачивания CSV файла');
  }
}

onMounted(fetchHackathons);
</script>

<template>
  <div class="dashboard-wrapper">
    <h1>Админ-панель: хакатоны</h1>
    <div v-if="loading">Загрузка...</div>
    <div v-else-if="error"><b style="color:red;">{{ error }}</b></div>
    <div v-else>
      <div class="table-wrapper">
        <table class="hacks-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Название</th>
            <th>Старт</th>
            <th>Финиш</th>
            <th>Статус</th>
            <th>Аналитика</th>
            <th>Экспорт</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="h in hackathons" :key="h.id">
            <td>{{ h.id }}</td>
            <td>{{ h.name }}</td>
            <td>{{ h.start_date?.slice(0,10) }}</td>
            <td>{{ h.end_date?.slice(0,10) }}</td>
            <td>{{ h.status }}</td>
            <td>
              <button @click="fetchAnalytics(h.id)">Аналитика</button>
            </td>
            <td>
              <button @click="downloadCSV(`http://localhost:8000/api/admin/${h.id}/participants/export`, `participants_${h.id}.csv`)" style="margin-bottom: 4px;">Участники CSV</button><br>
              <button @click="downloadCSV(`http://localhost:8000/api/admin/${h.id}/teams/export`, `teams_${h.id}.csv`)">Команды CSV</button>
            </td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>
    <div v-if="analyticsLoading" style="margin-top:2rem;">Загрузка аналитики...</div>
    <div v-else-if="analyticsError" style="color: red;">Ошибка аналитики: {{ analyticsError }}</div>
    <div v-else-if="analytics" class="analytics-block">
      <h2>Аналитика по хакатону</h2>
      <ul>
        <li>Всего участников: <b>{{ analytics.total_participants }}</b></li>
        <li>Всего команд: <b>{{ analytics.total_teams }}</b></li>
        <li>Участников без команды: <b>{{ analytics.participants_without_team }}</b></li>
        <li>Участников в командах: <b>{{ analytics.participants_in_team }}</b></li>
        <li>Средний размер команды: <b>{{ analytics.average_team_size }}</b></li>
        <li>
          Навыки:<ul>
            <li v-for="(cnt, skill) in analytics.skills_frequency" :key="skill">{{ skill }}: {{ cnt }}</li>
          </ul>
        </li>
        <li>
          Опыт:<ul>
            <li v-for="(cnt, lvl) in analytics.experience_distribution" :key="lvl">{{ lvl }}: {{ cnt }}</li>
          </ul>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.dashboard-wrapper {
  max-width: 1100px;
  width: 100%;
  margin: 1rem auto;
  padding: 1rem;
  background: #181818;
  border-radius: 15px;
  color: #eee;
}
.dashboard-wrapper h1 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}
.table-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  margin-top: 1.5rem;
}
.hacks-table {
  width: 100%;
  min-width: 800px;
  border-collapse: collapse;
}
.hacks-table th, .hacks-table td {
  border: 1px solid #333;
  padding: 0.5rem 0.7rem;
  font-size: 0.9rem;
}
.hacks-table th {
  background: #202058;
  white-space: nowrap;
}
@media (min-width: 768px) {
  .dashboard-wrapper {
    margin: 2rem auto;
    padding: 2rem;
  }
  .dashboard-wrapper h1 {
    font-size: 2rem;
    margin-bottom: 2rem;
  }
  .table-wrapper {
    margin-top: 2rem;
  }
  .hacks-table th, .hacks-table td {
    padding: 0.7rem 1rem;
    font-size: 1rem;
  }
}
button {
  padding: 0.4rem 0.8rem;
  margin-bottom: 4px;
  background: #0083d6;
  color: #fff;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-size: 0.85rem;
  white-space: nowrap;
}
@media (min-width: 768px) {
  button {
    padding: 0.4rem 1.2rem;
    font-size: 1rem;
  }
}
.analytics-block {
  margin-top: 2.5rem;
  background: #25253e;
  padding: 1.2rem 2rem;
  border-radius: 10px;
}
</style>
