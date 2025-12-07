import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  // Загружаем env-файлы из текущей директории (process.cwd())
  // Третий аргумент '' означает, что мы грузим все переменные,
  // либо можно оставить пустым, чтобы грузить только с префиксом VITE_
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [vue()],
    server: {
      port: 3000,
      open: true,
      proxy: {
        '/api': {
          // Теперь обращаемся к env объекту, который мы загрузили
          target: env.BACKEND_URL, 
          changeOrigin: true,
          secure: false,
        },
      },
    },
  }
})