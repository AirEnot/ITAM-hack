<template>
  <div class="home-welcome-text">
    <h1>ITAM Hack Platform</h1>
    <p>Веб-платформа для поиска, создания и управления командами для хакатонов.<br>
      <b>Реализация в процессе.</b>
    </p>
    <ul>
      <li><router-link to="/auth">Вход через Telegram</router-link></li>
      <li><router-link to="/profile">Профиль пользователя</router-link></li>
      <li><router-link to="/hackathons">Список хакатонов</router-link></li>
      <li><router-link to="/team">Моя команда</router-link></li>
      <li><router-link to="/admin/login">Вход в админку</router-link></li>
    </ul>
    <div style="margin-top: 2rem; color: #888; font-size: 0.97rem;">
      code design & development: <b>team BDC</b>
    </div>
  </div>
</template>

<style scoped>
.home-welcome-text {
  text-align: center;
  padding: 2rem 1rem 2rem 1rem;
}
.home-welcome-text h1 {
  font-size: 1.8rem;
  font-weight: bold;
  letter-spacing: 1.5px;
  margin-bottom: 1rem;
  color: #70bfff;
}
@media (min-width: 640px) {
  .home-welcome-text {
    padding: 3rem 0 2rem 0;
  }
  .home-welcome-text h1 {
    font-size: 2.1rem;
    letter-spacing: 2.1px;
    margin-bottom: 1.2rem;
  }
}
.home-welcome-text ul {
  margin: 2.2rem auto 1rem auto;
  padding: 0;
  list-style: none;
  max-width: 340px;
}
.home-welcome-text li {
  margin-bottom: 1.1rem;
}
.home-welcome-text a {
  color: #fff;
  padding: 0.65rem 1.5rem;
  background: #24244b;
  border-radius: 7px;
  font-size: 1.05rem;
  text-decoration: none;
  transition: background 0.16s;
  display: inline-block;
}
.home-welcome-text a:hover {
  color: #60b7ff;
  background: #252553;
}
</style>

