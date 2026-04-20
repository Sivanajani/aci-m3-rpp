import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/aci-m3-rpp/',   // must match the GitHub repo name
})
