import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/axios'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const accessToken = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')

  const isAuthenticated = computed(() => !!accessToken.value)

  async function register(data: object) {
    const response = await api.post('/auth/register/', data)
    setAuth(response.data)
    return response.data
  }

  async function login(credentials: object) {
    const response = await api.post('/auth/login/', credentials)
    setAuth(response.data)
    return response.data
  }

  async function logout() {
    try {
      await api.post('/auth/logout/', { refresh: refreshToken.value })
    } catch {}
    clearAuth()
  }

  function setAuth(data: any) {
    user.value = data.user
    accessToken.value = data.tokens.access
    refreshToken.value = data.tokens.refresh
    localStorage.setItem('user', JSON.stringify(data.user))
    localStorage.setItem('access_token', data.tokens.access)
    localStorage.setItem('refresh_token', data.tokens.refresh)
  }

  function clearAuth() {
    user.value = null
    accessToken.value = ''
    refreshToken.value = ''
    localStorage.clear()
  }

  return {
    user, accessToken, isAuthenticated,
    register, login, logout,
  }
})