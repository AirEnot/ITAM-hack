<template>
  <nav class="mobile-nav">
    <a href="/hackathons">🏆<span>Хакатоны</span></a>
    <a href="/team">👥<span>Команда</span></a>
    <a href="/profile">👤<span>Профиль</span></a>
  </nav>
</template>

<style scoped lang="css">
.mobile-nav {
  display: flex;
  position: fixed;
  left: 0;
  bottom: 0;
  width: 100vw;
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
.mobile-nav a:hover {
  background: #252553;
  color: #60b7ff;
}

@media (min-width: 800px) {
  .mobile-nav {
    display: none;
  }
}
</style>

