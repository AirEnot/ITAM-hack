import { defineStore } from 'pinia';
import { ref } from 'vue';
import { adminApiClient } from '../utils/api';

export const useAdminStore = defineStore('admin', () => {
  const hackathons = ref<any[]>([]);
  const analytics = ref<any>(null);
  const loading = ref(false);
  const error = ref('');

  async function fetchHackathons() {
    loading.value = true;
    error.value = '';
    try {
      const response = await adminApiClient.get('/api/admin/hackathons');
      hackathons.value = response.data;
      return response.data;
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e?.message || 'Ошибка загрузки хакатонов';
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function fetchAnalytics(hackathonId: number) {
    loading.value = true;
    error.value = '';
    try {
      const response = await adminApiClient.get(`/api/admin/${hackathonId}/analytics`);
      analytics.value = response.data;
      return response.data;
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e?.message || 'Ошибка загрузки аналитики';
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function createHackathon(data: any) {
    loading.value = true;
    error.value = '';
    try {
      const response = await adminApiClient.post('/api/hackathons', data);
      hackathons.value.push(response.data);
      return response.data;
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e?.message || 'Ошибка создания хакатона';
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function updateHackathon(hackathonId: number, data: any) {
    loading.value = true;
    error.value = '';
    try {
      const response = await adminApiClient.put(`/api/hackathons/${hackathonId}`, data);
      const index = hackathons.value.findIndex(h => h.id === hackathonId);
      if (index !== -1) {
        hackathons.value[index] = response.data;
      }
      return response.data;
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e?.message || 'Ошибка обновления хакатона';
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function exportParticipants(hackathonId: number): Promise<Blob> {
    try {
      const response = await adminApiClient.get(`/api/admin/${hackathonId}/participants/export`, {
        responseType: 'blob',
      });
      return response.data;
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e?.message || 'Ошибка экспорта участников';
      throw e;
    }
  }

  async function exportTeams(hackathonId: number): Promise<Blob> {
    try {
      const response = await adminApiClient.get(`/api/admin/${hackathonId}/teams/export`, {
        responseType: 'blob',
      });
      return response.data;
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e?.message || 'Ошибка экспорта команд';
      throw e;
    }
  }

  function clearData() {
    hackathons.value = [];
    analytics.value = null;
    error.value = '';
  }

  return {
    hackathons,
    analytics,
    loading,
    error,
    fetchHackathons,
    fetchAnalytics,
    createHackathon,
    updateHackathon,
    exportParticipants,
    exportTeams,
    clearData,
  };
});

