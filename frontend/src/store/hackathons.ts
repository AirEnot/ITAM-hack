import { defineStore } from 'pinia';
import { ref } from 'vue';
import apiClient from '../utils/api';

export const useHackathonsStore = defineStore('hackathons', () => {
  const hackathons = ref<any[]>([]);
  const currentHackathon = ref<any>(null);
  const loading = ref(false);
  const error = ref('');

  async function fetchHackathons() {
    loading.value = true;
    error.value = '';
    try {
      const response = await apiClient.get('/api/hackathons');
      hackathons.value = response.data;
      return response.data;
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e?.message || 'Ошибка загрузки хакатонов';
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function fetchHackathon(id: number) {
    loading.value = true;
    error.value = '';
    try {
      const response = await apiClient.get(`/api/hackathons/${id}`);
      currentHackathon.value = response.data;
      return response.data;
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e?.message || 'Ошибка загрузки хакатона';
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function registerForHackathon(hackathonId: number) {
    loading.value = true;
    error.value = '';
    try {
      await apiClient.post(`/api/hackathons/${hackathonId}/register`);
      // Обновляем текущий хакатон
      await fetchHackathon(hackathonId);
      return true;
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e?.message || 'Ошибка регистрации';
      throw e;
    } finally {
      loading.value = false;
    }
  }

  function clearHackathons() {
    hackathons.value = [];
    currentHackathon.value = null;
    error.value = '';
  }

  return {
    hackathons,
    currentHackathon,
    loading,
    error,
    fetchHackathons,
    fetchHackathon,
    registerForHackathon,
    clearHackathons,
  };
});

