<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '../../utils/api';

const invitations = ref<any[]>([]);
const loading = ref(false);
const error = ref('');

async function loadInvitations() {
  loading.value = true;
  error.value = '';
  try {
    const response = await apiClient.get('/api/invitations', {
      params: { status_filter: 'pending' },
    });
    invitations.value = response.data;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || 'Ошибка';
  } finally {
    loading.value = false;
  }
}

async function respondToInvitation(invitationId: number, accept: boolean) {
  try {
    await apiClient.post(`/api/invitations/${invitationId}/accept`, {
      accept
    });
    alert(accept ? 'Приглашение принято!' : 'Приглашение отклонено');
    loadInvitations();
  } catch (e: any) {
    alert(e?.response?.data?.detail || e?.message || 'Ошибка');
  }
}

onMounted(loadInvitations);
</script>

<template>
  <div class="invitations-list">
    <h1>Мои приглашения</h1>
    <div v-if="loading">Загрузка...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="invitations.length === 0" class="empty">Нет приглашений</div>
    <div v-else class="invitations-grid">
      <div v-for="invitation in invitations" :key="invitation.id" class="invitation-card">
        <h3>Приглашение в команду: {{ invitation.team?.name }}</h3>
        <p v-if="invitation.team?.description">{{ invitation.team.description }}</p>
        <div class="inviter">
          <strong>От:</strong> {{ invitation.sent_by?.full_name }}
        </div>
        <div class="actions">
          <button @click="respondToInvitation(invitation.id, true)" class="btn-accept">Принять</button>
          <button @click="respondToInvitation(invitation.id, false)" class="btn-decline">Отклонить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.invitations-list {
  max-width: 800px;
  margin: 0 auto;
}
.invitations-list h1 {
  color: #4cc5fc;
  margin-bottom: 2rem;
}
.invitations-grid {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.invitation-card {
  background: #1e1e2e;
  border-radius: 12px;
  padding: 1.5rem;
  color: #ececec;
}
.invitation-card h3 {
  color: #4cc5fc;
  margin-bottom: 0.5rem;
}
.inviter {
  color: #b8b8d4;
  margin: 1rem 0;
}
.actions {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  margin-top: 1rem;
}
@media (min-width: 640px) {
  .actions {
    flex-direction: row;
    gap: 1rem;
  }
}
.btn-accept,
.btn-decline {
  flex: 1;
  padding: 0.7rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
}
.btn-accept {
  background: #2a3e2a;
  color: #7fcf7f;
}
.btn-decline {
  background: #3e2a2a;
  color: #cf7f7f;
}
.error {
  color: #ff6b6b;
  text-align: center;
  padding: 2rem;
}
.empty {
  text-align: center;
  color: #888;
  padding: 3rem;
  background: #1e1e2e;
  border-radius: 12px;
}
</style>

