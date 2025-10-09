import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true,
    cors: true
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          mediapipe: ['@mediapipe/face_detection', '@mediapipe/camera_utils'],
          ui: ['react-color', 'react-dropzone', 'lucide-react']
        }
      }
    }
  },
  optimizeDeps: {
    include: ['@mediapipe/face_detection', '@mediapipe/camera_utils']
  }
})