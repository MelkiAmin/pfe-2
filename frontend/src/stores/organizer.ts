import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/axios'

export const useOrganizerStore = defineStore('organizer', () => {
  const organizer = ref(JSON.parse(localStorage.getItem('organizer') || 'null'))
  const token = ref(localStorage.getItem('organizer_access_token') || '')

  const isAuthenticated = computed(() => !!token.value)

  function logout() {
    organizer.value = null
    token.value = ''
    localStorage.removeItem('organizer')
    localStorage.removeItem('organizer_access_token')
    localStorage.removeItem('organizer_refresh_token')
  }

  return { organizer, token, isAuthenticated, logout }
})