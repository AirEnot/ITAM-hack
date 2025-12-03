import { ref } from 'vue';
import apiClient from '../utils/api';

/**
 * Composable для работы с приглашениями
 */
export function useInvitations() {
  const invitations = ref<any[]>([]);
  const loading = ref(false);
  const error = ref('');

  async function fetchInvitations(statusFilter: string = 'pending') {
    loading.value = true;
    error.value = '';
    try {
      const response = await apiClient.get('/api/invitations', {
        params: { status_filter: statusFilter },
      });
      invitations.value = response.data;
      return response.data;
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e?.message || 'Ошибка загрузки приглашений';
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function respondToInvitation(invitationId: number, accept: boolean) {
    loading.value = true;
    error.value = '';
    try {
      await apiClient.post(`/api/invitations/${invitationId}/accept`, {
        accept,
      });
      // Обновляем список приглашений
      await fetchInvitations();
      return true;
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e?.message || 'Ошибка обработки приглашения';
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function fetchParticipants(hackathonId: number) {
    loading.value = true;
    error.value = '';
    try {
      const response = await apiClient.get(`/api/users/hackathons/${hackathonId}/participants`);
      return response.data;
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e?.message || 'Ошибка загрузки участников';
      throw e;
    } finally {
      loading.value = false;
    }
  }

  return {
    invitations,
    loading,
    error,
    fetchInvitations,
    respondToInvitation,
    fetchParticipants,
  };
}

