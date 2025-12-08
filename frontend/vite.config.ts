import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  // Загружаем env-файлы из текущей директории (process.cwd())
  // Третий аргумент '' означает, что мы грузим все переменные,
  // либо можно оставить пустым, чтобы грузить только с префиксом VITE_
  const env = loadEnv(mode, process.cwd(), '')
  const backendTarget = env.VITE_BACKEND_URL || env.BACKEND_URL || 'http://localhost:8000'

  return {
    plugins: [vue()],
    server: {
      port: 3000,
      open: true,
      proxy: {
        '/api': {
          // Используем адрес backend из env
          target: backendTarget, 
          changeOrigin: true,
          secure: false,
        },
      },
    },
  }
})