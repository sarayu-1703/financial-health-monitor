import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: '../public',   // build goes to root /public, served by Vercel as static
    emptyOutDir: true,
  },
  server: {
    proxy: {
      '/api': 'http://localhost:8000'  // dev proxy to FastAPI
    }
  }
})
