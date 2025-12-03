<template>
  <div class="app-layout">
    <header class="main-header">
      <div class="container">
        <router-link to="/" class="logo">ITAM HACK</router-link>
        <nav class="main-nav">
          <router-link to="/hackathons">Хакатоны</router-link>
          <router-link to="/team">Моя команда</router-link>
          <router-link to="/profile">Профиль</router-link>
        </nav>
      </div>
    </header>
    <main class="main-content">
      <router-view />
    </main>
    <footer class="main-footer">
      <span>© ITAM Hack Platform 2025</span>
    </footer>
    <!-- Мобильная навигация -->
    <nav class="mobile-nav">
      <router-link to="/hackathons">🏆<span>Хакатоны</span></router-link>
      <router-link to="/team">👥<span>Моя команда</span></router-link>
      <router-link to="/profile">👤<span>Профиль</span></router-link>
    </nav>
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #18191c;
  color: #ededed;
}
.main-header {
  background: #24244b;
  padding: 0.3rem 0;
}
.logo {
  font-weight: bold;
  font-size: 1.3rem;
  letter-spacing: 1.5px;
  color: #60b7ff;
  margin-right: 2rem;
}
.main-header .container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.logo {
  font-size: 1.1rem;
  margin-right: 1rem;
}
.main-nav {
  display: none;
}
.main-nav a {
  margin-left: 2rem;
  color: #ededed;
  text-decoration: none;
  font-size: 1.05rem;
  position: relative;
}
.main-nav a.router-link-active {
  color: #60b7ff;
}
.main-nav a::after {
  content: '';
  display: block;
  width: 0; height: 2px;
  background: #60b7ff;
  transition: width .3s;
  position: absolute;
  left: 0; bottom: -3px;
}
.main-nav a:hover::after,
.main-nav a.router-link-active::after {
  width: 100%;
}

.main-content {
  flex: 1;
  max-width: 1100px;
  width: 100%;
  margin: 0 auto;
  padding: 1.5rem 1rem 5rem 1rem;
}
.main-footer {
  text-align: center;
  font-size: 0.95rem;
  background: #222237;
  padding: 0.8rem;
  color: #aaa;
  font-weight: 400;
}
.mobile-nav {
  display: flex;
  position: fixed;
  left: 0; bottom: 0; width: 100vw;
  background: #23233c;
  border-top: 1px solid #33334c;
  justify-content: space-around;
  padding: 0.3rem 0 0.1rem 0;
  z-index: 31;
}
.mobile-nav a {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  font-size: 1.25rem;
  color: #ededed;
  text-decoration: none;
  padding: 0.3rem 0.1rem;
  transition: background 0.15s;
}
.mobile-nav a span {
  font-size: 0.72rem;
}
.mobile-nav a:hover,
.mobile-nav a.router-link-active {
  background: #252553;
  color: #60b7ff;
}
@media (min-width: 768px) {
  .main-header .container {
    padding: 0 1.4rem;
  }
  .logo {
    font-size: 1.3rem;
    margin-right: 2rem;
  }
  .main-nav {
    display: flex;
  }
  .mobile-nav {
    display: none;
  }
  .main-content {
    padding: 2rem 1.1rem 2rem 1.1rem;
  }
}
@media (min-width: 1024px) {
  .main-content {
    padding: 2rem 1.5rem;
  }
}
</style>
