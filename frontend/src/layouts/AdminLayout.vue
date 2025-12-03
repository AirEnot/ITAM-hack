<template>
  <div class="admin-layout">
    <header class="admin-header">
      <div class="admin-header-content">
        <h1>Админ-панель ITAM Hack</h1>
        <nav class="admin-nav">
          <router-link to="/admin">Дашборд</router-link>
          <router-link to="/admin/hackathons">Хакатоны</router-link>
        </nav>
      </div>
    </header>
    <main class="admin-main">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.admin-layout {
  min-height: 100vh;
  background: #0f0f1a;
  color: #ececec;
}
.admin-header {
  background: #1a1a2e;
  border-bottom: 2px solid #2a2a3e;
  padding: 1rem 0;
}
.admin-header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.admin-header h1 {
  font-size: 1.5rem;
  color: #4cc5fc;
  margin: 0;
}
.admin-nav {
  display: flex;
  gap: 2rem;
}
.admin-nav a {
  color: #b8b8d4;
  text-decoration: none;
  font-size: 1.05rem;
  transition: color 0.15s;
}
.admin-nav a:hover,
.admin-nav a.router-link-active {
  color: #4cc5fc;
}
.admin-main {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}
@media (max-width: 1280px) {
  .admin-header-content {
    flex-direction: column;
    gap: 1rem;
  }
}
</style>

