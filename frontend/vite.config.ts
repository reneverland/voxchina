import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 8400,
    host: '0.0.0.0',
    allowedHosts: ['llmhi.com', 'www.llmhi.com', '.llmhi.com', 'localhost'],
    cors: true,
    headers: {
      'Access-Control-Allow-Origin': '*',
    },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8300',
        changeOrigin: true,
        secure: false
      },
      '/static': {
        target: 'http://127.0.0.1:8300',
        changeOrigin: true,
        secure: false
      }
    }
  }
})
