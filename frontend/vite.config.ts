import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Permite acesso de qualquer IP na rede
    port: 3000,
    strictPort: false,
    allowedHosts: [
      'bsmart.ngrok.app',
      'projectmanager.ngrok.app',
      '.ngrok.app', // Permite qualquer subdomínio ngrok.app
      '.ngrok-free.app', // Permite ngrok gratuito também
    ],
    proxy: {
      '/api': {
        target: 'http://localhost:8086',
        changeOrigin: true,
        secure: false,
        ws: true,
      },
    },
  },
})
