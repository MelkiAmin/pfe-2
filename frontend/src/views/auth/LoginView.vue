<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-8">

      <!-- Logo -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-indigo-600">HotelMate</h1>
        <p class="text-gray-500 mt-2">Connectez-vous à votre compte</p>
      </div>

      <!-- Erreur -->
      <div v-if="error" class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg mb-4 text-sm">
        {{ error }}
      </div>

      <!-- Formulaire -->
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Nom d'utilisateur</label>
          <input
            v-model="form.username"
            type="text"
            placeholder="Votre username"
            required
            class="w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Mot de passe</label>
          <div class="relative">
            <input
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="Votre mot de passe"
              required
              class="w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <button type="button" @click="showPassword = !showPassword"
              class="absolute right-3 top-3 text-gray-400 text-sm">
              {{ showPassword ? '🙈' : '👁️' }}
            </button>
          </div>
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 rounded-lg transition duration-200 disabled:opacity-50"
        >
          {{ loading ? 'Connexion...' : 'Se connecter' }}
        </button>
      </form>

      <!-- Liens -->
      <div class="mt-6 text-center text-sm text-gray-500 space-y-2">
        <p>
          Pas encore de compte ?
          <RouterLink to="/register" class="text-indigo-600 font-medium hover:underline">S'inscrire</RouterLink>
        </p>
        <p>
          Vous êtes organisateur ?
          <RouterLink to="/organizer/login" class="text-indigo-600 font-medium hover:underline">Login Organisateur</RouterLink>
        </p>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'

const router = useRouter()
const auth = useAuthStore()
const toast = useToast()

const form = ref({ username: '', password: '' })
const loading = ref(false)
const error = ref('')
const showPassword = ref(false)

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    await auth.login(form.value)
    toast.success('Connexion réussie !')
    router.push('/dashboard')
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Identifiants incorrects.'
  } finally {
    loading.value = false
  }
}
</script>