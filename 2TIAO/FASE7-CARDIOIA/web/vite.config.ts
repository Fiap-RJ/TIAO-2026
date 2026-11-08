import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // o recharts sozinho passa de 500 kB; o app é pequeno o bastante para um bundle só
  build: { chunkSizeWarningLimit: 800 },
})
