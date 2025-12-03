import { ref } from 'vue';
import apiClient, { adminApiClient } from '../utils/api';

/**
 * Composable для работы с API запросами
 */
export function useApi() {
  const loading = ref(false);
  const error = ref('');

  async function request<T>(
    fn: () => Promise<T>,
    errorMessage?: string
  ): Promise<T | null> {
    loading.value = true;
    error.value = '';
    try {
      const result = await fn();
      return result;
    } catch (e: any) {
      error.value = errorMessage || e?.response?.data?.detail || e?.message || 'Ошибка';
      return null;
    } finally {
      loading.value = false;
    }
  }

  return {
    loading,
    error,
    request,
  };
}

/**
 * Composable для работы с админскими API запросами
 */
export function useAdminApi() {
  const loading = ref(false);
  const error = ref('');

  async function request<T>(
    fn: () => Promise<T>,
    errorMessage?: string
  ): Promise<T | null> {
    loading.value = true;
    error.value = '';
    try {
      const result = await fn();
      return result;
    } catch (e: any) {
      error.value = errorMessage || e?.response?.data?.detail || e?.message || 'Ошибка';
      return null;
    } finally {
      loading.value = false;
    }
  }

  return {
    loading,
    error,
    request,
  };
}

export { apiClient, adminApiClient };

