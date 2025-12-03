import { defineStore } from 'pinia';
import { ref } from 'vue';
import apiClient from '../utils/api';

export const useUserStore = defineStore('user', () => {
  const profile = ref<any>(null);
  const loading = ref(false);
  const error = ref('');

  async function fetchProfile(userId?: number) {
    loading.value = true;
    error.value = '';
    try {
      const url = userId ? `/api/users/${userId}` : '/api/users/me';
      const response = await apiClient.get(url);
      profile.value = response.data;
      return response.data;
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e?.message || 'Ошибка загрузки профиля';
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function updateProfile(data: any) {
    loading.value = true;
    error.value = '';
    try {
      const response = await apiClient.put('/api/users/me', data);
      profile.value = response.data;
      return response.data;
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e?.message || 'Ошибка обновления профиля';
      throw e;
    } finally {
      loading.value = false;
    }
  }

  function clearProfile() {
    profile.value = null;
    error.value = '';
  }

  return {
    profile,
    loading,
    error,
    fetchProfile,
    updateProfile,
    clearProfile,
  };
});

