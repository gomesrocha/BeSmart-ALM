import axios from 'axios'

// Detecta automaticamente a URL base:
// 1. Se VITE_API_URL está definido (ngrok), usa ele
// 2. Senão, usa o proxy local /api/v1
const getBaseURL = () => {
  const envUrl = import.meta.env.VITE_API_URL
  if (envUrl) {
    console.log('🌐 Using API URL from environment:', envUrl)
    return envUrl
  }
  console.log('🏠 Using local proxy:', '/api/v1')
  return '/api/v1'
}

const api = axios.create({
  baseURL: getBaseURL(),
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
