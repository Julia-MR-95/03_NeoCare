import axios from 'axios'

//base URL desde variable de entorno (Vite usa VITE_ prefix)
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const apiClient = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
})

//interceptor: añade el JWT token a cada petición privada
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

//interceptor: si el token expiró (401), redirige al login guardando dónde estábamos
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      //redirige a dónde íbamos reconstruyendo la ruta
      const currentPath = window.location.pathname + window.location.search
      if (currentPath !== '/login/') {
        window.location.href = `/login?redirect=${encodeURIComponent(currentPath)}`
      } else {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default apiClient