import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const backendTarget = process.env.VITE_BACKEND_PROXY_URL || 'http://localhost:8000';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: '0.0.0.0',
    watch: {
      usePolling: true,
    },
    proxy: {
      '/admin': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/health': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/storage': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/sample_assets': {
        target: backendTarget,
        changeOrigin: true,
      },
    },
  },
});
