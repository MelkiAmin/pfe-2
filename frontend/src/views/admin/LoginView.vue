<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-8">

      <div class="text-center mb-8">
        <div class="w-16 h-16 bg-gray-900 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <span class="text-white text-2xl">🛡️</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-800">Administration</h1>
        <p class="text-gray-500 mt-1 text-sm">Accès réservé aux administrateurs</p>
      </div>

      <div v-if="error" class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg mb-4 text-sm">
        {{ error }}
      </div>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Nom d'utilisateur</label>
          <input v-model="form.username" type="text" placeholder="admin" required
            class="w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-gray-500" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Mot de passe</label>
          <input v-model="form.password" type="password" placeholder="••••••••" required
            class="w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-gray-500" />
        </div>
        <button type="submit" :disabled="loading"
          class="w-full bg-gray-900 hover:bg-gray-800 text-white font-semibold py-3 rounded-lg transition disabled:opacity-50">
          {{ loading ? 'Connexion...' : 'Accéder au panneau' }}
        </button>
      </form>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import adminApi from '@/api/adminAxios'

const router = useRouter()
const form = ref({ username: '', password: '' })
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    const response = await adminApi.post('/admin/login/', form.value)
    localStorage.setItem('admin_access_token', response.data.tokens.access)
    localStorage.setItem('admin_refresh_token', response.data.tokens.refresh)
    localStorage.setItem('admin', JSON.stringify(response.data.admin))
    router.push('/admin/dashboard')
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Identifiants incorrects.'
  } finally {
    loading.value = false
  }
}
</script>