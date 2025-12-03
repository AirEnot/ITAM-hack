import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { isUserAuthenticated, isAdminAuthenticated } from '../utils/auth';
import apiClient from '../utils/api';

export const useAuthStore = defineStore('auth', () => {
  const user = ref<any>(null);
  const admin = ref<any>(null);
  const loading = ref(false);

  const isAuthenticated = computed(() => isUserAuthenticated());
  const isAdmin = computed(() => isAdminAuthenticated());

  async function fetchUser() {
    if (!isUserAuthenticated()) return;
    loading.value = true;
    try {
      const response = await apiClient.get('/api/users/me');
      user.value = response.data;
    } catch (error) {
      console.error('Failed to fetch user:', error);
      user.value = null;
    } finally {
      loading.value = false;
    }
  }

  function clearUser() {
    user.value = null;
  }

  function clearAdmin() {
    admin.value = null;
  }

  return {
    user,
    admin,
    loading,
    isAuthenticated,
    isAdmin,
    fetchUser,
    clearUser,
    clearAdmin,
  };
});

