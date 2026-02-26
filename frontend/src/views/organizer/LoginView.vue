<template>
  <div class="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-8">

      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-purple-600">HotelMate</h1>
        <p class="text-gray-500 mt-2">Espace Organisateur</p>
      </div>

      <div v-if="error" class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg mb-4 text-sm">
        {{ error }}
      </div>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Nom d'utilisateur</label>
          <input v-model="form.username" type="text" placeholder="username" required
            class="w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Mot de passe</label>
          <input v-model="form.password" type="password" placeholder="Mot de passe" required
            class="w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500" />
        </div>
        <button type="submit" :disabled="loading"
          class="w-full bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 rounded-lg transition disabled:opacity-50">
          {{ loading ? 'Connexion...' : 'Se connecter' }}
        </button>
      </form>

      <div class="mt-6 text-center text-sm text-gray-500">
        <RouterLink to="/login" class="text-purple-600 hover:underline">← Retour connexion utilisateur</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import api from '@/api/axios'

const router = useRouter()
const toast = useToast()

const form = ref({ username: '', password: '' })
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    const response = await api.post('/organizer/login/', form.value)
    localStorage.setItem('organizer_access_token', response.data.tokens.access)
    localStorage.setItem('organizer_refresh_token', response.data.tokens.refresh)
    localStorage.setItem('organizer', JSON.stringify(response.data.organizer))
    toast.success('Connexion réussie !')
    router.push('/organizer/dashboard')
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Identifiants incorrects.'
  } finally {
    loading.value = false
  }
}
</script>