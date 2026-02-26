import axios from 'axios'

const organizerApi = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

organizerApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('organizer_access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

organizerApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('organizer_access_token')
      window.location.href = '/organizer/login'
    }
    return Promise.reject(error)
  }
)

export default organizerApi