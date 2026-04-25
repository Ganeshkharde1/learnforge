// Axios client with X-User-ID header injection
import axios from 'axios'
import { useAuthStore } from '../store/authStore'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// Inject X-User-ID on every request
apiClient.interceptors.request.use((config) => {
  const userId = useAuthStore.getState().userId
  if (userId) {
    config.headers['X-User-ID'] = userId
  }
  return config
})

// Global error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.message ||
      'An unexpected error occurred'
    return Promise.reject(new Error(message))
  }
)

export const API_BASE = BASE_URL
